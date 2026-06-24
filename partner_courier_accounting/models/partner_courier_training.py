from urllib.parse import parse_qs, urlparse

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PartnerCourierTraining(models.Model):
    _name = 'partner.courier.training'
    _description = 'Kurye Eğitimi'
    _order = 'sequence, id desc'

    name = fields.Char(string='Eğitim Adı', required=True)
    sequence = fields.Integer(string='Sıra', default=10)
    active = fields.Boolean(string='Aktif', default=True)
    description = fields.Text(string='Açıklama')
    content_type = fields.Selection([
        ('video_url', 'Video Linki'),
        ('video_file', 'Video Dosyası'),
        ('document', 'Doküman'),
    ], string='İçerik Tipi', required=True, default='video_url')
    video_url = fields.Char(string='Video Linki')
    video_embed_url = fields.Char(
        string='Gömülü Video Linki',
        compute='_compute_video_embed_url',
    )
    video_file = fields.Binary(string='Video Dosyası', attachment=True)
    video_filename = fields.Char(string='Video Dosya Adı')
    document_attachment_ids = fields.Many2many(
        'ir.attachment',
        'partner_courier_training_document_rel',
        'training_id',
        'attachment_id',
        string='Dokümanlar',
    )
    attendance_ids = fields.One2many(
        'partner.courier.training.attendance',
        'training_id',
        string='Eğitime Katılan Kuryeler',
        readonly=True,
    )
    attendance_count = fields.Integer(
        string='Katılım Sayısı',
        compute='_compute_attendance_count',
    )

    @api.depends('attendance_ids')
    def _compute_attendance_count(self):
        grouped = self.env['partner.courier.training.attendance'].read_group(
            [('training_id', 'in', self.ids)],
            ['training_id'],
            ['training_id'],
        )
        counts = {item['training_id'][0]: item['training_id_count'] for item in grouped}
        for training in self:
            training.attendance_count = counts.get(training.id, 0)

    @api.depends('video_url')
    def _compute_video_embed_url(self):
        for training in self:
            training.video_embed_url = training._get_embed_url(training.video_url)

    @api.constrains('content_type', 'video_url', 'video_file', 'document_attachment_ids')
    def _check_training_content(self):
        for training in self:
            if training.content_type == 'video_url':
                parsed = urlparse(training.video_url or '')
                if parsed.scheme not in ('http', 'https') or not parsed.netloc:
                    raise ValidationError('Video linki geçerli bir HTTP/HTTPS adresi olmalıdır.')
            elif training.content_type == 'video_file' and not training.video_file:
                raise ValidationError('Video dosyası içerik tipinde video dosyası yüklenmelidir.')
            elif training.content_type == 'document' and not training.document_attachment_ids:
                raise ValidationError('Doküman içerik tipinde en az bir doküman yüklenmelidir.')

    def _get_embed_url(self, url):
        if not url:
            return False
        parsed = urlparse(url)
        host = (parsed.netloc or '').lower()
        path = parsed.path or ''
        if 'youtube.com' in host:
            video_id = parse_qs(parsed.query).get('v', [False])[0]
            if video_id:
                return 'https://www.youtube.com/embed/%s' % video_id
            if path.startswith('/embed/'):
                return url
            if path.startswith('/shorts/'):
                return 'https://www.youtube.com/embed/%s' % path.split('/')[2]
        if 'youtu.be' in host and path.strip('/'):
            return 'https://www.youtube.com/embed/%s' % path.strip('/').split('/')[0]
        if 'vimeo.com' in host and path.strip('/').isdigit():
            return 'https://player.vimeo.com/video/%s' % path.strip('/')
        return url

    def action_view_attendances(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Eğitime Katılan Kuryeler',
            'res_model': 'partner.courier.training.attendance',
            'view_mode': 'tree,form',
            'domain': [('training_id', '=', self.id)],
            'context': {'default_training_id': self.id},
        }


class PartnerCourierTrainingAttendance(models.Model):
    _name = 'partner.courier.training.attendance'
    _description = 'Kurye Eğitim Katılımı'
    _order = 'attended_at desc, id desc'

    training_id = fields.Many2one(
        'partner.courier.training',
        string='Eğitim',
        required=True,
        ondelete='cascade',
        index=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Kurye',
        required=True,
        ondelete='cascade',
        index=True,
    )
    attended_at = fields.Datetime(
        string='Katılım Tarihi',
        required=True,
        default=fields.Datetime.now,
        readonly=True,
    )

    _sql_constraints = [
        (
            'training_partner_unique',
            'unique(training_id, partner_id)',
            'Bir kurye aynı eğitime yalnızca bir kez katılabilir.',
        ),
    ]
