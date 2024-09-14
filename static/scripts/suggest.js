document.addEventListener('DOMContentLoaded', function() {
    const fromInput = document.getElementById('from');
    const fromDatalist = document.getElementById('stations-from');

    const toInput = document.getElementById('to');
    const toDatalist = document.getElementById('stations-to');

    const fetchSuggestions = async (query) => {
        if (query.length < 3) return [];
        try {
            const response = await fetch(`/suggest?sample=${query}`);
            if (!response.ok) throw new Error('Network response was not ok');
            const stations = await response.json();
            return stations;
        } catch (error) {
            console.error('Error fetching suggestions:', error);
            return [];
        }
    };

    const showSuggestions = async (query, datalist) => {
        const stations = await fetchSuggestions(query);
        datalist.innerHTML = '';
        stations.forEach(station => {
            const option = document.createElement('option');
            option.value = station;
            datalist.appendChild(option);
        });
    };

    const inputHandler = function(e) {
        showSuggestions(e.target.value, e.target.list);
    };

    fromInput.addEventListener('input', inputHandler);
    toInput.addEventListener('input', inputHandler);
});
