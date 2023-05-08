const options = {
    Camera: ['Sony A7III', 'Sony A7III lens 105', 'Panasonic DC-S5'],
    Rec: ['Rode micro mic'],
    Apple: ['iPad Pro', 'MacBook Pro'],
    Tripod: ['Manfrotto 1004BAC-3', 'Manfrotto 1052BAC', 'Manfrotto 190X', 'Manfrotto BeFree Advanced'],
    Projectors: ['CP-X3021WN', 'CP-EX250N-EF', 'CP-WX4022WN-GF', 'CP-X3042WN-EF', 'CP-X300EF', 'CP-X2510N-EF'],
    Cables: ['AC', 'HDMI 5M', 'Micro Hdmi', 'SDI 12G', 'SDI 6G', 'PL TRS', 'VGA', 'XLR', 'XLR To PL 1/8\"'],
    Lights: ['FalconEyes BL-30TD II', 'FalconEyes RX-24TDX', 'GODOX M1'],
    Convertors: ['HDMI to SDI 3G', 'BiDirectional SDI HDMI 12G']
};

const type_drop = document.getElementById('type_drop');
const model_drop = document.getElementById('model_drop');

// Event listener for when the first dropdown value changes
type_drop.addEventListener('change', () => {
    // Clear the options in the second dropdown
    model_drop.innerHTML = '<option value="">-- בחר ציוד --</option>';
    // Get the selected value of the first dropdown
    const selectedValue = type_drop.value;

    // Populate the second dropdown with options based on the selected value
    options[selectedValue].forEach(optionValue => {
        const option = document.createElement('option');
        option.value = optionValue;
        option.textContent = optionValue;
        model_drop.appendChild(option);
    });
});