document.addEventListener("DOMContentLoaded", function () {
    const carousel = document.getElementById("showcaseCarousel");
    if (!carousel) return;

    const track = carousel.querySelector(".carousel-track");
    const slides = Array.from(track.querySelectorAll(".carousel-slide"));
    const prevButton = carousel.querySelector(".prev");
    const nextButton = carousel.querySelector(".next");
    const dots = Array.from(document.querySelectorAll("#carouselDots .dot"));

    const txtViewer = document.getElementById("showcaseTxtViewer");
    const txtFileName = document.getElementById("txtFileName");

    let currentIndex = 0;

    function updateCarousel() {
        track.style.transform = `translateX(-${currentIndex * 100}%)`;

        dots.forEach((dot, index) => {
            dot.classList.toggle("active", index === currentIndex);
        });

        updateTxtPanel();
    }

    function updateTxtPanel() {
        const currentSlide = slides[currentIndex];
        const txtPath = currentSlide.dataset.txt;

        if (!txtPath || !txtViewer || !txtFileName) return;

        const fileName = txtPath.split("/").pop();
        txtFileName.textContent = fileName;
        txtViewer.textContent = "Loading...";

        fetch(txtPath)
            .then(response => {
                if (!response.ok) {
                    throw new Error("TXT file not found");
                }
                return response.text();
            })
            .then(text => {
                txtViewer.textContent = text.trim() ? text : "This txt file is empty.";
                txtViewer.scrollTop = 0;
            })
            .catch(() => {
                txtViewer.textContent = "Failed to load the coordinate txt file.";
            });
    }

    function goToSlide(index) {
        if (index < 0) {
            currentIndex = slides.length - 1;
        } else if (index >= slides.length) {
            currentIndex = 0;
        } else {
            currentIndex = index;
        }
        updateCarousel();
    }

    function nextSlide() {
        goToSlide(currentIndex + 1);
    }

    function prevSlide() {
        goToSlide(currentIndex - 1);
    }

    if (prevButton) {
        prevButton.addEventListener("click", function () {
            prevSlide();
        });
    }

    if (nextButton) {
        nextButton.addEventListener("click", function () {
            nextSlide();
        });
    }

    dots.forEach((dot, index) => {
        dot.addEventListener("click", function () {
            goToSlide(index);
        });
    });

    updateCarousel();
});
