document.addEventListener("DOMContentLoaded", function() {

    // ===== Visitor Popup =====
    const visitorPopupShown = sessionStorage.getItem('visitor_popup_shown');
    if (!visitorPopupShown) {
        const popup = document.createElement('div');
        popup.innerHTML = `
            <div class="position-fixed top-50 start-50 translate-middle p-4 bg-white rounded shadow-lg"
                 style="z-index:1050; max-width:400px;">
                <h5>Welcome!</h5>
                <form id="visitor-popup-form" method="POST">
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

        document.getElementById('visitor-popup-form').addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(this);
            const csrftoken = document.body.dataset.csrfToken; // set in <body> from Django

            fetch("/visitor-popup-submit/", {
                    method: "POST",
                    headers: { "X-CSRFToken": csrftoken },
                    body: formData
                })
                .then(res => {
                    if (res.redirected) {
                        // Visitor created, session set; reload page to reflect name
                        window.location.href = res.url;
                    }
                });

            sessionStorage.setItem('visitor_popup_shown', 'true');
            popup.remove();
        });
    }

    // ===== Hero Carousel Auto Slide =====
    const heroCarousel = document.querySelector('#heroCarousel');
    if (heroCarousel) {
        new bootstrap.Carousel(heroCarousel, { interval: 5000, ride: 'carousel' });
    }

    // ===== Venue Map & Selection =====
    const mapElement = document.getElementById('venueMap');
    if (mapElement) {
        let map = L.map('venueMap').setView([40.7583, -73.9876], 15);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(map);
        let marker = L.marker([40.7583, -73.9876]).addTo(map);

        const venueButtons = document.querySelectorAll('.select-venue-btn');
        const selectedVenue = document.getElementById('selectedVenue');
        const baseAmount = document.getElementById('baseAmount');
        const inventoryList = document.getElementById('inventoryList');
        const totalAmount = document.getElementById('totalAmount');

        let venueInventory = {};
        const inventoryData = document.getElementById("venueInventoryData");
        if (inventoryData) {
            try {
                venueInventory = JSON.parse(inventoryData.textContent);
            } catch (e) {
                console.warn("Invalid venue inventory JSON", e);
            }
        }

        function updateInventory(venueId) {
            const items = venueInventory[venueId] || [];
            inventoryList.innerHTML = "";
            if (items.length > 0) {
                items.forEach(item => {
                    let text = `${item.item_name}: ${item.quantity}`;
                    if (item.type) text += ` (${item.type})`;
                    const li = document.createElement("li");
                    li.textContent = text;
                    inventoryList.appendChild(li);
                });
            } else {
                inventoryList.innerHTML = "<li>No inventory available</li>";
            }
        }

        venueButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                const venueId = this.dataset.venueId;
                const name = this.dataset.venueName;
                const base = parseFloat(this.dataset.venueBase) || 0;
                const lat = parseFloat(this.dataset.venueLat) || 40.7583;
                const lng = parseFloat(this.dataset.venueLng) || -73.9876;

                selectedVenue.textContent = name;
                baseAmount.textContent = base.toFixed(2);
                totalAmount.textContent = base.toFixed(2);

                updateInventory(venueId);

                map.setView([lat, lng], 15);
                marker.setLatLng([lat, lng]);

                const requisitionId = document.body.dataset.requisitionId;
                const saveUrl = document.body.dataset.saveVenueUrl;
                const csrfToken = document.body.dataset.csrfToken;

                if (requisitionId && saveUrl && csrfToken) {
                    fetch(saveUrl, {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "X-CSRFToken": csrfToken,
                        },
                        body: JSON.stringify({ requisition_id: requisitionId, venue_id: venueId })
                    });
                }
            });
        });

        // Auto-select first venue if available
        if (venueButtons.length > 0) venueButtons[0].click();
    }

    // ===== Extra: Carousel Click Updates Event Name =====
    const slides = document.querySelectorAll('#eventsHeroCarousel .carousel-item img');
    const header = document.getElementById('eventNameHeader');
    slides.forEach(slide => {
        slide.addEventListener('click', function() {
            const name = this.getAttribute('data-event-name');
            if (name && header) {
                header.textContent = name + ' - Booking Info';
            }
        });
    });

});