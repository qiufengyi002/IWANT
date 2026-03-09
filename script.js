const CONFIG = {
    API_KEY: '',
    USE_MOCK_DATA: true,
    REFRESH_INTERVAL: 30000,
};

const MOCK_STOCKS = {
    AAPL: { name: 'Apple Inc.', price: 178.52, change: 2.34, changePercent: 1.33, open: 176.18, high: 179.23, low: 175.89, volume: 52340000 },
    GOOGL: { name: 'Alphabet Inc.', price: 141.80, change: -0.92, changePercent: -0.64, open: 142.72, high: 143.50, low: 140.88, volume: 18900000 },
    MSFT: { name: 'Microsoft Corporation', price: 378.91, change: 4.56, changePercent: 1.22, open: 374.35, high: 380.12, low: 373.88, volume: 21450000 },
    TSLA: { name: 'Tesla, Inc.', price: 248.50, change: -5.23, changePercent: -2.06, open: 253.73, high: 255.00, low: 246.80, volume: 98700000 },
    AMZN: { name: 'Amazon.com, Inc.', price: 178.25, change: 1.87, changePercent: 1.06, open: 176.38, high: 179.50, low: 175.92, volume: 35600000 },
    NVDA: { name: 'NVIDIA Corporation', price: 875.28, change: 15.42, changePercent: 1.79, open: 859.86, high: 878.90, low: 857.23, volume: 42100000 },
    META: { name: 'Meta Platforms, Inc.', price: 505.75, change: 8.32, changePercent: 1.67, open: 497.43, high: 507.20, low: 495.80, volume: 15200000 },
    BABA: { name: 'Alibaba Group', price: 75.42, change: -1.28, changePercent: -1.67, open: 76.70, high: 77.15, low: 75.00, volume: 8900000 },
};

const MOCK_INDICES = {
    DOW: { value: 38996.39, change: 125.69, changePercent: 0.32 },
    NASDAQ: { value: 16091.92, change: -28.50, changePercent: -0.18 },
    SP500: { value: 5096.27, change: 8.96, changePercent: 0.18 },
};

let watchlist = JSON.parse(localStorage.getItem('watchlist')) || ['AAPL', 'GOOGL', 'TSLA'];
let priceChart = null;
let currentSymbol = null;

function init() {
    loadMarketIndices();
    loadWatchlist();
    setupEventListeners();
    setInterval(refreshData, CONFIG.REFRESH_INTERVAL);
}

function setupEventListeners() {
    document.getElementById('searchBtn').addEventListener('click', searchStock);
    document.getElementById('searchInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchStock();
    });
}

function loadMarketIndices() {
    if (CONFIG.USE_MOCK_DATA) {
        updateIndexDisplay('dow', MOCK_INDICES.DOW);
        updateIndexDisplay('nasdaq', MOCK_INDICES.NASDAQ);
        updateIndexDisplay('sp500', MOCK_INDICES.SP500);
        updateTimestamp();
    }
}

function updateIndexDisplay(id, data) {
    const valueEl = document.getElementById(`${id}Value`);
    const changeEl = document.getElementById(`${id}Change`);
    
    valueEl.textContent = formatNumber(data.value);
    changeEl.textContent = `${data.change >= 0 ? '+' : ''}${formatNumber(data.change)} (${data.changePercent >= 0 ? '+' : ''}${data.changePercent}%)`;
    changeEl.className = `index-change ${data.change >= 0 ? 'positive' : 'negative'}`;
}

function loadWatchlist() {
    const container = document.getElementById('watchlist');
    container.innerHTML = '';
    
    if (watchlist.length === 0) {
        container.innerHTML = '<p class="loading">自选股为空，搜索股票并添加到自选股</p>';
        return;
    }

    watchlist.forEach(symbol => {
        const stock = getStockData(symbol);
        if (stock) {
            container.appendChild(createStockCard(symbol, stock));
        }
    });
}

function getStockData(symbol) {
    if (CONFIG.USE_MOCK_DATA) {
        const baseStock = MOCK_STOCKS[symbol.toUpperCase()];
        if (baseStock) {
            const variation = (Math.random() - 0.5) * 2;
            return {
                ...baseStock,
                price: baseStock.price * (1 + variation / 100),
                change: baseStock.change + variation,
            };
        }
        return {
            name: `${symbol.toUpperCase()} Corporation`,
            price: (Math.random() * 500 + 50).toFixed(2),
            change: (Math.random() * 10 - 5).toFixed(2),
            changePercent: (Math.random() * 4 - 2).toFixed(2),
            open: (Math.random() * 500 + 50).toFixed(2),
            high: (Math.random() * 500 + 50).toFixed(2),
            low: (Math.random() * 500 + 50).toFixed(2),
            volume: Math.floor(Math.random() * 100000000),
        };
    }
    return null;
}

function createStockCard(symbol, stock) {
    const card = document.createElement('div');
    card.className = 'stock-card';
    card.innerHTML = `
        <div class="stock-info">
            <h3>${symbol.toUpperCase()}</h3>
            <p>${stock.name}</p>
        </div>
        <div class="stock-price">
            <span class="price">$${formatNumber(stock.price)}</span>
            <span class="change ${stock.change >= 0 ? 'positive' : 'negative'}">
                ${stock.change >= 0 ? '+' : ''}${formatNumber(stock.change)} (${stock.changePercent >= 0 ? '+' : ''}${stock.changePercent}%)
            </span>
        </div>
        <button class="remove-btn" onclick="removeFromWatchlist('${symbol}', event)">移除</button>
    `;
    card.addEventListener('click', (e) => {
        if (!e.target.classList.contains('remove-btn')) {
            showStockDetail(symbol);
        }
    });
    return card;
}

function searchStock() {
    const input = document.getElementById('searchInput');
    const symbol = input.value.trim().toUpperCase();
    
    if (!symbol) return;
    
    const stock = getStockData(symbol);
    if (stock) {
        showStockDetail(symbol);
        if (!watchlist.includes(symbol)) {
            const addBtn = document.createElement('button');
            addBtn.className = 'add-watchlist';
            addBtn.textContent = '添加到自选股';
            addBtn.onclick = () => addToWatchlist(symbol);
            const detailSection = document.getElementById('stockDetail');
            const existingBtn = detailSection.querySelector('.add-watchlist');
            if (existingBtn) existingBtn.remove();
            detailSection.appendChild(addBtn);
        }
    }
    input.value = '';
}

function showStockDetail(symbol) {
    currentSymbol = symbol;
    const stock = getStockData(symbol);
    if (!stock) return;

    document.getElementById('stockDetail').style.display = 'block';
    document.getElementById('detailSymbol').textContent = symbol.toUpperCase();
    document.getElementById('detailName').textContent = stock.name;
    document.getElementById('detailPrice').textContent = `$${formatNumber(stock.price)}`;
    
    const changeEl = document.getElementById('detailChange');
    changeEl.textContent = `${stock.change >= 0 ? '+' : ''}${formatNumber(stock.change)} (${stock.changePercent >= 0 ? '+' : ''}${stock.changePercent}%)`;
    changeEl.className = `change ${stock.change >= 0 ? 'positive' : 'negative'}`;
    
    document.getElementById('detailOpen').textContent = `$${formatNumber(stock.open)}`;
    document.getElementById('detailHigh').textContent = `$${formatNumber(stock.high)}`;
    document.getElementById('detailLow').textContent = `$${formatNumber(stock.low)}`;
    document.getElementById('detailVolume').textContent = formatVolume(stock.volume);
    
    renderChart(symbol);
    document.getElementById('stockDetail').scrollIntoView({ behavior: 'smooth' });
}

function renderChart(symbol) {
    const ctx = document.getElementById('priceChart').getContext('2d');
    
    if (priceChart) {
        priceChart.destroy();
    }

    const labels = [];
    const data = [];
    const basePrice = parseFloat(getStockData(symbol).price);
    
    for (let i = 29; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }));
        const variation = (Math.random() - 0.5) * 0.1;
        data.push((basePrice * (1 + variation)).toFixed(2));
    }
    data.push(basePrice);

    priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: `${symbol} 价格`,
                data: data,
                borderColor: '#00d4ff',
                backgroundColor: 'rgba(0, 212, 255, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 5,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(26, 26, 46, 0.9)',
                    titleColor: '#00d4ff',
                    bodyColor: '#fff',
                    borderColor: 'rgba(0, 212, 255, 0.3)',
                    borderWidth: 1,
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.5)',
                        maxTicksLimit: 7,
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.5)',
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
}

function addToWatchlist(symbol) {
    if (!watchlist.includes(symbol)) {
        watchlist.push(symbol);
        localStorage.setItem('watchlist', JSON.stringify(watchlist));
        loadWatchlist();
        const addBtn = document.querySelector('.add-watchlist');
        if (addBtn) addBtn.remove();
    }
}

function removeFromWatchlist(symbol, event) {
    event.stopPropagation();
    watchlist = watchlist.filter(s => s !== symbol);
    localStorage.setItem('watchlist', JSON.stringify(watchlist));
    loadWatchlist();
}

function refreshData() {
    loadMarketIndices();
    loadWatchlist();
    if (currentSymbol) {
        showStockDetail(currentSymbol);
    }
    updateTimestamp();
}

function updateTimestamp() {
    document.getElementById('updateTime').textContent = new Date().toLocaleString('zh-CN');
}

function formatNumber(num) {
    return parseFloat(num).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

function formatVolume(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(2) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(2) + 'K';
    }
    return num.toString();
}

document.addEventListener('DOMContentLoaded', init);
