console.log("Story2 WEB");

console.log("Story2 WEB");

fetch('/webstory/data', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({})
})
.then(response => {
    console.log("ilk then", response);
    if (!response.ok) {
        throw new Error("HTTP error " + response.status);
    }
    return response.json(); // Yanıtı JSON olarak işleyin
})
.then(data => {
    console.log("ikinci then", data);
    if (!data || !data.result || !data.result.data) {
        throw new Error("Geçersiz veri formatı");
    }
    console.log(data.result.data);
    var allStories = data.result.data.map(function(item) {
        return {
            thumbUrl: '/web/image?model=webstory.profile&id=' + item.id + '&field=webstory_image_small',
            imageUrl: '/web/image?model=webstory.profile&id=' + item.id + '&field=webstory_image_big',
            title: item.name,
        };
    });
    initializeStories(allStories);
})
.catch(error => {
    console.error("Veri çekilirken bir hata oluştu:", error);
});

// Dinamik olarak hikaye verilerini yükleme ve ekranda gösterme fonksiyonu
function initializeStories(allStories) {
    const storiesContainer = document.querySelector(".stories-container");
    const storyFull = document.querySelector(".story-full");
    const storyFullImage = document.querySelector(".story-full img");
    const storyFullTitle = document.querySelector(".story-full .title");
    const closeBtn = document.querySelector(".story-full .close-btn");
    const leftArrow = document.querySelector(".story-full .left-arrow");
    const rightArrow = document.querySelector(".story-full .right-arrow");

    let currentIndex = 0;
    let timer;

    allStories.forEach((s, i) => {
        const content = document.createElement("div");
        content.classList.add("content");

        const img = document.createElement("img");
        img.setAttribute("src", s.thumbUrl);

        storiesContainer.appendChild(content);
        content.appendChild(img);

        content.addEventListener("click", () => {
            currentIndex = i;
            storyFull.classList.add("active");
            storyFullImage.setAttribute("src", s.imageUrl);

            if (!s.title) {
                storyFullTitle.style.display = "none";
            } else {
                storyFullTitle.style.display = "block";
                storyFullTitle.innerHTML = s.title;
            }

            clearInterval(timer);
            timer = setInterval(nextStory, 5000);
        });
    });

    closeBtn.addEventListener("click", () => {
        storyFull.classList.remove("active");
    });

    leftArrow.addEventListener("click", () => {
        if (currentIndex > 0) {
            currentIndex -= 1;

            storyFullImage.setAttribute("src", allStories[currentIndex].imageUrl);

            if (!allStories[currentIndex].title) {
                storyFullTitle.style.display = "none";
            } else {
                storyFullTitle.style.display = "block";
                storyFullTitle.innerHTML = allStories[currentIndex].title;
            }

            clearInterval(timer);
            timer = setInterval(nextStory, 5000);
        }
    });

    const nextStory = () => {
        if (currentIndex < allStories.length - 1) {
            currentIndex += 1;

            storyFullImage.setAttribute("src", allStories[currentIndex].imageUrl);

            if (!allStories[currentIndex].title) {
                storyFullTitle.style.display = "none";
            } else {
                storyFullTitle.style.display = "block";
                storyFullTitle.innerHTML = allStories[currentIndex].title;
            }
        }
    };

    rightArrow.addEventListener("click", () => {
        nextStory();
        clearInterval(timer);
        timer = setInterval(nextStory, 5000);
    });
}
