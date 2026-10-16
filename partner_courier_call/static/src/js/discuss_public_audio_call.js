/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import { attr } from '@mail/model/model_field';
import { clear, insert } from '@mail/model/model_field_command';

registerPatch({
    name: 'DiscussPublicView',
    recordMethods: {
        /**
         * Opens the full-screen call as audio-only. The camera remains
         * available from the standard call controls after joining.
         *
         * @override
         */
        async switchToThreadView() {
            if (!this.startAudioOnly) {
                return this._super(...arguments);
            }
            document.body.classList.add('pcc-call-in-progress');
            this.update({
                threadViewer: {
                    extraClass: 'flex-grow-1',
                    hasMemberList: true,
                    hasThreadView: true,
                    hasTopbar: true,
                    thread: this.channel,
                },
                welcomeView: clear(),
            });
            if (this.isChannelTokenSecret) {
                window.history.replaceState(
                    window.history.state,
                    null,
                    `/discuss/channel/${this.channel.id}${window.location.search}`
                );
            }
            if (this.channel.defaultDisplayMode === 'video_full_screen') {
                await this.channel.toggleCall({ startWithVideo: false });
                this.threadView.callView.update({ isFullScreen: true });
            }
        },

        /** @override */
        switchToWelcomeView() {
            if (!this.startAudioOnly) {
                return this._super(...arguments);
            }
            this.update({
                threadViewer: clear(),
                welcomeView: {
                    channel: this.channel,
                    isDoFocusGuestNameInput: true,
                    originalGuestName: this.messaging.currentGuest && this.messaging.currentGuest.name,
                    pendingGuestName: this.messaging.currentGuest && this.messaging.currentGuest.name,
                },
            });
            this.messaging.browser.setTimeout(async () => {
                if (!this.exists() || !this.welcomeView || this.isCourierAutoJoining) {
                    return;
                }
                this.update({ isCourierAutoJoining: true });
                try {
                    await this.welcomeView.joinChannel();
                } catch (_error) {
                    if (this.exists()) {
                        this.update({ isCourierAutoJoining: false });
                    }
                }
            }, 0);
        },
    },
    fields: {
        startAudioOnly: attr({
            default: false,
            readonly: true,
        }),
        isEndingCourierCall: attr({
            default: false,
        }),
        isCourierAutoJoining: attr({
            default: false,
        }),
    },
});

registerPatch({
    name: 'WelcomeView',
    recordMethods: {
        /** @override */
        onClickJoinButton() {
            if (this.discussPublicView && this.discussPublicView.startAudioOnly) {
                document.body.classList.add('pcc-call-in-progress');
            }
            return this._super(...arguments);
        },

    },
});

registerPatch({
    name: 'Rtc',
    recordMethods: {
        /**
         * Join the server-side call without creating a microphone track or an
         * offer while this participant is alone. Both participants first
         * prepare their tracks, then exactly one of them creates the offer.
         *
         * @override
         */
        async initSession({ currentSessionId, iceServers, startWithAudio, startWithVideo, videoType = 'user-video' }) {
            const publicView = this.messaging.discussPublicView;
            if (!publicView || !publicView.startAudioOnly) {
                return this._super(...arguments);
            }
            if (this.courierAudioSyncTimeout) {
                this.messaging.browser.clearTimeout(this.courierAudioSyncTimeout);
            }
            this.reset();
            this.update({
                currentRtcSession: insert({ id: currentSessionId }),
                courierAudioSyncTimeout: clear(),
                isCourierAudioPreparing: false,
                isCourierAudioReady: false,
                isCourierMicrophonePromptVisible: false,
                isCourierMicrophoneRequestPending: false,
                hasCourierMicrophonePermissionError: false,
                shouldCourierStartWithAudio: false,
                iceServers: iceServers || this.iceServers,
            });
            this.currentRtcSession.update({ isSelfMuted: true });
            await this.messaging.rpc({
                route: '/mail/rtc/session/update_and_broadcast',
                params: {
                    session_id: this.currentRtcSession.id,
                    values: {
                        is_camera_on: this.currentRtcSession.isCameraOn,
                        is_deaf: this.currentRtcSession.isDeaf,
                        is_muted: true,
                        is_screen_sharing_on: this.currentRtcSession.isScreenSharingOn,
                    },
                },
            }, { shadow: true });
            this._scheduleCourierAudioSynchronization(0);
            if (startWithVideo) {
                await this._toggleVideoBroadcast({ type: videoType });
            }
        },

        _scheduleCourierAudioSynchronization(delay = 100) {
            if (this.courierAudioSyncTimeout) {
                this.messaging.browser.clearTimeout(this.courierAudioSyncTimeout);
            }
            this.update({
                courierAudioSyncTimeout: this.messaging.browser.setTimeout(
                    this._synchronizeCourierAudioConnection.bind(this),
                    delay
                ),
            });
        },

        async _synchronizeCourierAudioConnection() {
            this.update({ courierAudioSyncTimeout: clear() });
            const publicView = this.messaging.discussPublicView;
            if (
                !publicView
                || !publicView.startAudioOnly
                || !this.channel
                || !this.currentRtcSession
            ) {
                return;
            }
            const remoteSessions = this.channel.rtcSessions.filter(
                (session) => session !== this.currentRtcSession
            );
            if (!remoteSessions.length) {
                return;
            }

            if (!this.audioTrack && !this.shouldCourierStartWithAudio) {
                this.update({ isCourierMicrophonePromptVisible: true });
                return;
            }

            if (
                this.shouldCourierStartWithAudio
                && !this.audioTrack
                && !this.isCourierAudioPreparing
            ) {
                this.update({ isCourierAudioPreparing: true });
                await this.updateLocalAudioTrack(true);
                if (!this.exists() || !this.currentRtcSession) {
                    return;
                }
                this.update({
                    isCourierAudioPreparing: false,
                    isCourierAudioReady: Boolean(this.audioTrack),
                    isCourierMicrophonePromptVisible: !this.audioTrack,
                    isCourierMicrophoneRequestPending: false,
                });
                if (!this.audioTrack) {
                    this.update({ hasCourierMicrophonePermissionError: true });
                    return;
                }
                // Odoo normally debounces this state for three seconds. The
                // readiness handshake must be immediate for the RTC offer.
                await this.messaging.rpc({
                    route: '/mail/rtc/session/update_and_broadcast',
                    params: {
                        session_id: this.currentRtcSession.id,
                        values: {
                            is_camera_on: this.currentRtcSession.isCameraOn,
                            is_deaf: this.currentRtcSession.isDeaf,
                            is_muted: false,
                            is_screen_sharing_on: this.currentRtcSession.isScreenSharingOn,
                        },
                    },
                }, { shadow: true });
            }
            if (!this.audioTrack) {
                return;
            }

            const allPeersHaveAudio = remoteSessions.every(
                (session) => !session.isSelfMuted
            );
            const isOfferInitiator = remoteSessions.every(
                (session) => Number(this.currentRtcSession.id) > Number(session.id)
            );
            const hasMissingConnection = remoteSessions.some(
                (session) => !session.rtcPeerConnection
                    || !session.rtcPeerConnection.peerConnection
            );
            if (allPeersHaveAudio && isOfferInitiator && hasMissingConnection) {
                this._callSessions();
            }

            let allConnectionsStable = true;
            for (const session of this.connectedRtcSessions) {
                const connection = session.rtcPeerConnection
                    && session.rtcPeerConnection.peerConnection;
                if (!connection || connection.signalingState !== 'stable') {
                    allConnectionsStable = false;
                    continue;
                }
                await session.updateRemoteTrack('audio');
                if (!['connected', 'completed'].includes(connection.iceConnectionState)) {
                    allConnectionsStable = false;
                }
            }
            if (!allPeersHaveAudio || hasMissingConnection || !allConnectionsStable) {
                this._scheduleCourierAudioSynchronization(750);
            }
        },

        async requestCourierMicrophone() {
            if (this.isCourierMicrophoneRequestPending) {
                return;
            }
            this.update({
                hasCourierMicrophonePermissionError: false,
                isCourierMicrophoneRequestPending: true,
                shouldCourierStartWithAudio: true,
            });
            await this._synchronizeCourierAudioConnection();
        },

        /** @override */
        async unmute() {
            const publicView = this.messaging.discussPublicView;
            const hasRemoteSession = this.channel
                && this.channel.rtcSessions.some(
                    (session) => session !== this.currentRtcSession
                );
            if (publicView && publicView.startAudioOnly && !hasRemoteSession) {
                this.update({ shouldCourierStartWithAudio: true });
                return;
            }
            return this._super(...arguments);
        },
    },
    fields: {
        courierAudioSyncTimeout: attr(),
        isCourierAudioPreparing: attr({ default: false }),
        isCourierAudioReady: attr({ default: false }),
        isCourierMicrophonePromptVisible: attr({ default: false }),
        isCourierMicrophoneRequestPending: attr({ default: false }),
        hasCourierMicrophonePermissionError: attr({ default: false }),
        shouldCourierStartWithAudio: attr({ default: false }),
    },
});

registerPatch({
    name: 'Thread',
    recordMethods: {
        /**
         * Start the audio readiness handshake when another participant enters.
         *
         * @override
         */
        updateRtcSessions(rtcSessions) {
            const result = this._super(...arguments);
            const publicView = this.messaging.discussPublicView;
            if (
                publicView
                && publicView.startAudioOnly
                && publicView.channel === this
                && this.rtc
                && this.rtc.currentRtcSession
            ) {
                this.rtc._scheduleCourierAudioSynchronization();
            }
            return result;
        },
    },
});

registerPatch({
    name: 'RtcSession',
    recordMethods: {
        _onChangeCourierAudioReadiness() {
            const rtc = this.messaging.rtc;
            const publicView = this.messaging.discussPublicView;
            if (
                publicView
                && publicView.startAudioOnly
                && rtc
                && rtc.currentRtcSession
                && this !== rtc.currentRtcSession
                && this.channel === rtc.channel
            ) {
                rtc._scheduleCourierAudioSynchronization();
            }
        },
    },
    onChanges: [{
        dependencies: ['isSelfMuted'],
        methodName: '_onChangeCourierAudioReadiness',
    }],
});

registerPatch({
    name: 'CallView',
    recordMethods: {
        async onClickRequestCourierMicrophone() {
            await this.messaging.rtc.requestCourierMicrophone();
        },
    },
});

registerPatch({
    name: 'CallActionListView',
    recordMethods: {
        async onClickEndCourierCall() {
            const publicView = this.messaging.discussPublicView;
            const config = window.pccCourierCall;
            if (!publicView || publicView.isEndingCourierCall || !config) {
                return;
            }
            publicView.update({ isEndingCourierCall: true });
            try {
                await window.pccEndCourierCall();
            } catch (_error) {
                publicView.update({ isEndingCourierCall: false });
                this.messaging.notify({
                    message: this.env._t('Görüşme sonlandırılamadı. Lütfen tekrar deneyin.'),
                    type: 'warning',
                });
            }
        },
    },
});
