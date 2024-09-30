document.addEventListener('DOMContentLoaded', function() {
    const rows = document.querySelectorAll('.clickable-row');

    rows.forEach(row => {
        row.addEventListener('click', function() {
            const name = this.getAttribute('data-name');

            // Redirect to the member profile page with the clicked name
            window.location.href = `/member_profile/${name}`;
        });
    });
});