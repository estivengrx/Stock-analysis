window.onload = function() {
    var table = document.querySelector('.table');
    if (table) {
        var rows = table.querySelectorAll('tr.table-info');
        var stocks = [];

        rows.forEach(function(row) {
            var stockName = row.cells[0].innerText;
            stocks.push(stockName);
        });

        if (stocks.length > 0) {
            Swal.fire({
                title: 'Analysis results',
                text: 'Based on your preferences, these stocks might be a good fit: ' + stocks.join(', '),
                icon: 'info',
                confirmButtonText: 'OK'
            });
        }
    }
};

$(function () {
    $('[data-toggle="tooltip"]').tooltip();
});

document.addEventListener('DOMContentLoaded', function () {
    const stockInput = document.getElementById('stock-input');
    const addStockButton = document.getElementById('add-stock');
    const stockList = document.getElementById('stock-list');
    const stocksField = document.getElementById('stocks');
    let stocks = [];

    addStockButton.addEventListener('click', function () {
        const stockCode = stockInput.value.trim().toUpperCase();
        if (stockCode && !stocks.includes(stockCode)) {
            stocks.push(stockCode);
            updateStockList();
            stockInput.value = '';
        }
    });

    stockList.addEventListener('click', function (e) {
        if (e.target.classList.contains('remove-stock')) {
            const stockCode = e.target.dataset.stock;
            stocks = stocks.filter(stock => stock !== stockCode);
            updateStockList();
        }
    });

    function updateStockList() {
        stockList.innerHTML = '';
        stocks.forEach(stock => {
            const stockItem = document.createElement('span');
            stockItem.className = 'badge badge-pill badge-secondary mr-2';
            stockItem.innerHTML = `${stock} <i class="fas fa-times remove-stock" data-stock="${stock}" style="cursor: pointer;"></i>`;
            stockList.appendChild(stockItem);
        });
        stocksField.value = stocks.join(',');
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const addStockButton = document.getElementById('add-stock');
    const stockInput = document.getElementById('stock-input');
    const stockList = document.getElementById('stock-list');
    const stocksInput = document.getElementById('stocks');
    const weightsInputs = document.querySelectorAll('.weight-input');

    function updateStocks() {
        const stocks = Array.from(stockList.children).map(item => item.textContent.trim());
        stocksInput.value = stocks.join(',');
    }

    addStockButton.addEventListener('click', function() {
        const stock = stockInput.value.trim().toUpperCase();
        if (stock) {
            const stockItem = document.createElement('span');
            stockItem.classList.add('badge', 'badge-secondary', 'mr-2');
            stockItem.textContent = stock;
            stockList.appendChild(stockItem);
            stockInput.value = '';
            updateStocks();
        }
    });

    // Ensure the weights sum to 100
    document.getElementById('analyze-form').addEventListener('submit', function(e) {
        let totalWeight = 0;
        weightsInputs.forEach(input => {
            totalWeight += parseFloat(input.value) || 0;
        });
        if (totalWeight !== 100) {
            e.preventDefault();
            Swal.fire({
                title: 'Invalid Weights',
                text: 'The total weight percentages must sum up to 100. Please adjust the weights.',
                icon: 'error',
                confirmButtonText: 'OK'
            });
        }
    });
});

document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll('.weight-input').forEach(input => {
        input.addEventListener('input', calculateTotalWeight);
    });
});

function calculateTotalWeight() {
    let totalWeight = 0;
    document.querySelectorAll('.weight-input').forEach(input => {
        totalWeight += parseFloat(input.value) || 0;
    });
    if (totalWeight > 100) {
        Swal.fire({
            title: 'Invalid Weights',
            text: 'The total weight percentages must not exceed 100. Please adjust the weights.',
            icon: 'error',
            confirmButtonText: 'OK'
        });
    } else {
        document.getElementById('total-weight').innerText = totalWeight + '%';
    }
}