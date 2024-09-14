const form = document.querySelector('#form');

const checkValidity = (input) => {
  input.classList.remove('text-field__input_valid');
  input.classList.remove('text-field__input_invalid');
  input.nextElementSibling.textContent = '';
  
  if (input.checkValidity()) {
    input.classList.add('text-field__input_valid');
    input.nextElementSibling.textContent = 'Отлично!';
  } else {
    input.classList.add('text-field__input_invalid');
    input.nextElementSibling.textContent = input.validationMessage;
  }
}

const checkNameValidity = (nameInput) => {
    const name = nameInput.value.trim();
  
    if (name.length < 2) {
      nameInput.setCustomValidity('Введите минимум 2 символа.');
    } else {
      nameInput.setCustomValidity('');
    }
}

const checkPasswordValidity = (passwordInput) => {
  const password = passwordInput.value.trim();
  
  if (password.length < 8) {
    passwordInput.setCustomValidity('Введите минимум 8 символов.');
  } else {
    passwordInput.setCustomValidity('');
  }
}

const onNameInput = (e) => {
    const target = e.target;
    if (target.id === 'firstname') {
      checkNameValidity(target);
    }
}

const onPasswordInput = (e) => {
  const target = e.target;
  if (target.id === 'password') {
    checkPasswordValidity(target);
  }
}

const checkValidityAll = () => {
  const inputs = form.querySelectorAll('input');
  inputs.forEach((input) => {
    checkValidity(input);
  });
}

const onCheckValidity = (e) => {
  const target = e.target;
  if (target.classList.contains('text-field__input')) {
    checkValidity(target);
  } else if (target.id === 'comment') {
    checkCommentLength(target);
  }
}

form.addEventListener('change', onCheckValidity);
form.addEventListener('keydown', onCheckValidity);
form.addEventListener('keyup', onCheckValidity);
form.addEventListener('input', onPasswordInput);
form.addEventListener('input', onNameInput);
checkValidityAll();

form.addEventListener('submit', (e) => {
  e.preventDefault();
  checkValidityAll();
});


  

  
  