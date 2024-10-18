
let currentInput = '0';
let currentOperation = null;
let previousInput = null;

function updateDisplay() {
    document.getElementById('display').textContent = currentInput;
}

function appendNumber(number) {
    if (currentInput === '0' && number !== '.') {
        currentInput = number;
    } else {
        currentInput += number;
    }
    updateDisplay();
}

function appendSymbol(symbol) {
    if (currentInput === '0') {
        currentInput = symbol;
    } else {
        currentInput += symbol;
    }
    updateDisplay();
}

function setOperation(op) {
    if (currentOperation !== null) {
        calculateResult();
    }
    previousInput = currentInput;
    currentInput = '0';
    currentOperation = op;
    updateDisplay();
}

function clearCalculator() {
    currentInput = '0';
    currentOperation = null;
    previousInput = null;
    updateDisplay();
}

function calculateResult() {
    if (currentOperation === null) {
        return;
    }

    let body = {};
    if (['add', 'subtract', 'multiply', 'divide'].includes(currentOperation)) {
        body = {
            operation: currentOperation,
            a: parseFloat(previousInput),
            b: parseFloat(currentInput)
        };
    } else if (['derivative', 'integral', 'solve', 'expand', 'factor'].includes(currentOperation)) {
        body = {
            operation: currentOperation,
            expression: currentInput
        };
    }

    fetch('/calculate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            currentInput = 'Error';
        } else {
            currentInput = data.result.toString();
        }
        currentOperation = null;
        previousInput = null;
        updateDisplay();
    })
    .catch(error => {
        console.error('Error:', error);
        currentInput = 'Error';
        updateDisplay();
    });
}

document.addEventListener('keydown', (event) => {
    if (event.key >= '0' && event.key <= '9' || event.key === '.') {
        appendNumber(event.key);
    } else if (event.key === '+') {
        setOperation('add');
    } else if (event.key === '-') {
        setOperation('subtract');
    } else if (event.key === '*') {
        setOperation('multiply');
    } else if (event.key === '/') {
        setOperation('divide');
    } else if (event.key === 'Enter' || event.key === '=') {
        calculateResult();
    } else if (event.key === 'Escape') {
        clearCalculator();
    } else if (event.key === 'x' || event.key === '(' || event.key === ')' || event.key === '^') {
        appendSymbol(event.key);
    }
});
