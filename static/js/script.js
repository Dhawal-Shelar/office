document.addEventListener("DOMContentLoaded", function() {

    // ===== Visitor Popup =====
    const visitorPopupShown = sessionStorage.getItem('visitor_popup_shown');
    if (!visitorPopupShown) {
        const popup = document.createElement('div');
        popup.innerHTML = `
            <div class="position-fixed top-50 start-50 translate-middle p-4 bg-white rounded shadow-lg" style="z-index:1050; max-width:400px;">
                <h5>Welcome!</h5>
                <form id="visitor-popup-form">
                    <div class="mb-2">
                        <label>First Name</label>
                        <input type="text" name="fname" class="form-control" required>
                    </div>
                    <div class="mb-2">
                        <label>Mobile</label>
                        <input type="text" name="mobile" class="form-control" required>
                    </div>
                    <button type="submit" class="btn btn-orange w-100 mt-2">Submit</button>
                </form>
            </div>
        `;
        document.body.appendChild(popup);

        document.getElementById('visitor-popup-form').addEventListener('submit', function(e){
            e.preventDefault();
            sessionStorage.setItem('visitor_popup_shown', 'true');
            popup.remove();
        });
    }

    // ===== Carousel Auto Slide =====
    const heroCarousel = document.querySelector('#heroCarousel');
    if (heroCarousel) {
        new bootstrap.Carousel(heroCarousel, {
            interval: 5000,
            ride: 'carousel'
        });
    }

});
