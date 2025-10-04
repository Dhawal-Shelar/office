document.addEventListener("DOMContentLoaded", function() {

    // ===== Hero Carousel Auto Slide =====
    const heroCarousel = document.querySelector('#eventsCarousel');
    if (heroCarousel) {
        new bootstrap.Carousel(heroCarousel, { interval: 5000, ride: 'carousel' });
    }

    // ===== Visitor Modal Popup =====
    const visitorModalEl = document.getElementById('visitorModal');
    if (visitorModalEl) {
        const visitorModal = new bootstrap.Modal(visitorModalEl);
        visitorModal.show();
    }

    // ===== Venue Selection (for information page) =====
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
        } catch (e) { console.warn("Invalid venue inventory JSON", e); }
    }

    function updateInventory(venueId) {
        const items = venueInventory[venueId] || [];
        if (!inventoryList) return;
        inventoryList.innerHTML = "";
        if (items.length) {
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
            const lat = parseFloat(this.dataset.venueLat) || 0;
            const lng = parseFloat(this.dataset.venueLng) || 0;

            if (selectedVenue) selectedVenue.textContent = name;
            if (baseAmount) baseAmount.textContent = base.toFixed(2);
            if (totalAmount) totalAmount.textContent = base.toFixed(2);

            updateInventory(venueId);

            // Update map if exists
            if (window.map && window.marker) {
                window.map.setView([lat, lng], 15);
                window.marker.setLatLng([lat, lng]);
            }

            // Save selection via AJAX
            const requisitionId = document.body.dataset.requisitionId;
            const saveUrl = document.body.dataset.saveVenueUrl;
            const csrfToken = document.body.dataset.csrfToken;
            if (requisitionId && saveUrl && csrfToken) {
                fetch(saveUrl, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken
                    },
                    body: JSON.stringify({ requisition_id: requisitionId, venue_id: venueId })
                });
            }
        });
    });

    if (venueButtons.length > 0) venueButtons[0].click();

});