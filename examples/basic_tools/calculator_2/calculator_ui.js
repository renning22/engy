
function createButton(text, onClick, className = '') {
    const button = document.createElement('button');
    button.textContent = text;
    button.onclick = onClick;
    button.className = `btn ${className}`;
    return button;
}

function setupNumpad() {
    const numpad = document.getElementById('numpad');
    const numpadLayout = [
        '7', '8', '9', ['/', 'btn-orange'], ['(', 'btn-blue'],
        '4', '5', '6', ['*', 'btn-orange'], [')', 'btn-blue'],
        '1', '2', '3', ['-', 'btn-orange'], ['^', 'btn-blue'],
        '0', '.', ['=', 'btn-green'], ['+', 'btn-orange'], ['x', 'btn-blue']
    ];

    numpadLayout.forEach(item => {
        if (typeof item === 'string') {
            numpad.appendChild(createButton(item, () => appendNumber(item)));
        } else {
            numpad.appendChild(createButton(item[0], item[0] === '=' ? calculateResult : () => appendSymbol(item[0]), item[1]));
        }
    });
}

function setupOperations() {
    const operations = document.getElementById('operations');
    const operationsLayout = [
        ['C', clearCalculator, 'btn-red'],
        ['d/dx', () => setOperation('derivative'), 'btn-purple'],
        ['∫ dx', () => setOperation('integral'), 'btn-purple'],
        ['Solve', () => setOperation('solve'), 'btn-purple'],
        ['=', () => appendSymbol('='), 'btn-blue']
    ];

    operationsLayout.forEach(([text, onClick, className]) => {
        operations.appendChild(createButton(text, onClick, className));
    });
}

function setupAdvancedOperations() {
    const advancedOperations = document.getElementById('advanced-operations');
    const advancedOperationsLayout = [
        ['Expand', () => setOperation('expand'), 'btn-purple'],
        ['Factor', () => setOperation('factor'), 'btn-purple']
    ];

    advancedOperationsLayout.forEach(([text, onClick, className]) => {
        advancedOperations.appendChild(createButton(text, onClick, className));
    });
}

document.addEventListener('DOMContentLoaded', () => {
    setupNumpad();
    setupOperations();
    setupAdvancedOperations();
});
