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

const checkCommentLength = (textarea) => {
  const minLength = 15;
  const length = textarea.value.trim().length;
  
  if (length >= minLength) {
    textarea.classList.remove('text-field__input_invalid');
    textarea.classList.add('text-field__input_valid');
    textarea.nextElementSibling.textContent = 'Отлично!';
  } else {
    textarea.classList.remove('text-field__input_valid');
    textarea.classList.add('text-field__input_invalid');
    textarea.nextElementSibling.textContent = `Минимальное количество символов: ${minLength}`;
  }
}

const checkValidityAll = () => {
  const inputs = form.querySelectorAll('input');
  inputs.forEach((input) => {
    checkValidity(input);
  });
  
  const commentTextarea = form.querySelector('#comment');
  checkCommentLength(commentTextarea);
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
checkValidityAll();

form.addEventListener('submit', (e) => {
  e.preventDefault();
  checkValidityAll();
});

/*
0. Создать бд и пользователя под проект!!!!
1. Установить питон
2. Через пип установить fastapi и библиотеки (написал в тг)
3. Создать новый проект и работать в нем
4. Создать папку static и закинуть фронт
Добавляются слеши (1 / - корень)
5. FastAPI, научиться получать запросы (откуда-нибудь)
6. Python, изучить указанные библиотеки
7. Научиться делать запросы через js в бэк
8. Научиться добавлять объекты на страницу через js
*/