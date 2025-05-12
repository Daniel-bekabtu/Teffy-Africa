
particlesJS('particles-js',
    {
        "particles": {
            "number": {
                "value": 30,
                "density": {
                    "enable": true,
                    "value_area": 800
                }
            },
            "color": {
                "value": "#1a8d5f"
            },
            "shape": {
                "type": "circle"
            },
            "opacity": {
                "value": 0.1,
                "random": true
            },
            "size": {
                "value": 3,
                "random": true
            },
            "line_linked": {
                "enable": false
            },
            "move": {
                "enable": true,
                "speed": 1,
                "direction": "bottom",
                "random": true,
                "straight": false,
                "out_mode": "out"
            }
        },
        "interactivity": {
            "detect_on": "canvas",
            "events": {
                "onhover": {
                    "enable": false
                },
                "onclick": {
                    "enable": false
                },
                "resize": true
            }
        },
        "retina_detect": true
    }
);
document.querySelectorAll('.menu-item').forEach(item => {
    item.addEventListener('click', () => {
        document.querySelectorAll('.menu-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
        const route = item.getAttribute('data-route');
        window.location.href = route;
    });
});
const menuContainer = document.querySelector('.menu-container');
let isScrolling = false;
let startX;
let scrollLeft;

menuContainer.addEventListener('mousedown', (e) => {
    isScrolling = true;
    startX = e.pageX - menuContainer.offsetLeft;
    scrollLeft = menuContainer.scrollLeft;
});

menuContainer.addEventListener('mouseleave', () => {
    isScrolling = false;
});

menuContainer.addEventListener('mouseup', () => {
    isScrolling = false;
});

menuContainer.addEventListener('mousemove', (e) => {
    if (!isScrolling) return;
    e.preventDefault();
    const x = e.pageX - menuContainer.offsetLeft;
    const walk = (x - startX) * 2;
    menuContainer.scrollLeft = scrollLeft - walk;
});
