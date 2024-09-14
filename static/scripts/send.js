// Функция для создания ячейки таблицы с классом 'route-cell'
function td(contents) {
    return "<td class='route-cell'>" + contents + "</td>";
}



// Функция для создания заголовка таблицы с классом 'route-cell'
function th(contents) {
    return "<th class='route-cell'>" + contents + "</th>";
}



// Функция для создания строки таблицы из элементов
function row(items) {
    return "<tr>" + items.join("") + "</tr>";
}



// Функция для форматирования времени из строки в формате ISO
function formatTime(isoString) {
    // Проверка на пустую строку
    if (!isoString) {
        return "";
    }
    // Создание объекта Date из строки
    const date = new Date(isoString);
    // Проверка на некорректную дату
    if (isNaN(date.getTime())) {
        return "";
    }
    // Добавление 3 часов к времени
    date.setHours(date.getHours() + 3);
    // Возвращение времени в формате "чч:мм"
    return date.toISOString().substring(11, 16);
}



// Функция для создания строки с информацией об остановке
function createStopRow(stop) {
    // Получение имени остановки
    const stopName = stop["name"];
    // Форматирование времени прибытия
    const arrivalTime = formatTime(stop["arrivalTime"]);
    // Форматирование времени отправления
    const departureTime = formatTime(stop["departureTime"]);
    // Создание строки таблицы с ячейками для имени остановки, времени прибытия и времени отправления
    return row([td(stopName), td(arrivalTime), td(departureTime)]);
}



// Функция для создания таблицы остановок
function createStopsTable(stops) {
    // Инициализация таблицы с заголовком
    let table = `<table class='stops-table'>
        ${row([th("Станция"), th("Время прибытия"), th("Время отправления")])}`;

    // Добавление строк остановок в таблицу
    stops.forEach(stop => {
        table += createStopRow(stop);
    });

    // Завершение таблицы
    table += `</table>`;
    return table;
}



// Функция для вычисления времени в пути между двумя моментами времени
function calculateTravelTime(departureTime, arrivalTime) {
    // Создание объектов Date из строк времени отправления и прибытия
    const departureDate = new Date(departureTime);
    const arrivalDate = new Date(arrivalTime);

    // Вычисление времени в пути в миллисекундах
    const travelTimeMs = arrivalDate - departureDate;

    // Преобразование времени в минуты
    const travelTimeMinutes = Math.floor(travelTimeMs / 60000);

    // Вычисление часов и минут
    const hours = Math.floor(travelTimeMinutes / 60);
    const minutes = travelTimeMinutes % 60;

    // Возвращение времени в формате "чч мм"
    return `${hours}ч ${minutes}м`;
}



// Функция для форматирования цены
function formatPrice(price) {
    // Преобразование цены из копеек в рубли с двумя знаками после запятой
    const rubles = (price / 100).toFixed(2).replace('.', ',');
    return rubles; // Возвращение отформатированной цены
}



// Функция для создания HTML-кода маршрута
function route(segment, index) {
    // Проверка наличия сегмента маршрута и наличия минимального количества остановок
    if (!segment || !segment.stops || segment.stops.length < 2) {
        return ''; // Возвращение пустой строки, если условия не выполняются
    }

    // Извлечение данных о сегменте маршрута
    const voyage_number = segment["voyage_number"];
    const stops = segment["stops"];
    const price = segment["price"];
    const formattedPrice = formatPrice(price);
    const departureStop = stops[0];
    const arrivalStop = stops[stops.length - 1];

    // Проверка наличия данных о начальной и конечной остановках
    if (!departureStop || !arrivalStop || !departureStop.name || !arrivalStop.name) {
        return ''; // Возвращение пустой строки, если условия не выполняются
    }

    // Извлечение данных о начальной остановке
    const departureStation = departureStop["name"];
    const departureTime = formatTime(departureStop["departureTime"]);
    const departureTimeISO = departureStop["departureTime"];

    // Извлечение данных о конечной остановке
    const arrivalStation = arrivalStop["name"];
    const arrivalTime = formatTime(arrivalStop["arrivalTime"]);
    const arrivalTimeISO = arrivalStop["arrivalTime"];

    // Вычисление количества промежуточных остановок
    const stopCount = stops.length - 2;
    const stopCountText = getStopCountText(stopCount);

    // Генерация уникального идентификатора для таблицы остановок
    const stopsTableId = `stops-table-${index}`;

    // Вычисление времени в пути
    const travelingTime = calculateTravelTime(departureTimeISO, arrivalTimeISO);

    // Формирование HTML-кода маршрута
    return `
        <div class="route-container">
            <div class="route-table">
                <div class="route-details">
                    <div>
                        <strong style="font-size: larger;">${voyage_number}</strong>
                    </div>
                    <div>
                        <strong>${departureTime}</strong><br>
                        ${departureStation}
                    </div>
                    <div class="arrow">
                        <strong>В пути ${travelingTime}</strong><br>
                        <svg width="150" height="20" viewBox="0 0 150 20" xmlns="http://www.w3.org/2000/svg">
                        <line x1="0" y1="10" x2="140" y2="10" stroke="black" stroke-width="2"/>
                        <polygon points="140,5 150,10 140,15" fill="black"/>
                        </svg>
                    </div>
                    <div>
                        <strong>${arrivalTime}</strong><br>
                        ${arrivalStation}
                    </div>
                    <div>
                        <strong>Самый дешевый билет</strong><br>
                        ₽${formattedPrice}
                    </div>
                    <div>
                        <button class="stop-button" onclick="toggleStops('${stopsTableId}')">${stopCountText}</button>
                    </div>
                </div>
                <div id="${stopsTableId}" style="display: none;">
                    ${createStopsTable(stops)}
                </div>
            </div>
        </div>`;
}



// Функция для получения времени самого раннего отправления из сегмента маршрута
function getEarliestDeparture(segment) {
    // Проверка наличия сегмента, остановок в сегменте и времени отправления для первой остановки
    if (segment && segment.stops && segment.stops.length > 0 && segment.stops[0].departureTime) {
        // Возвращение времени отправления в виде объекта Date
        return new Date(segment.stops[0].departureTime);
    } else {
        // Возвращение null, если условия не выполняются
        return null;
    }
}



// Функция для переключения отображения таблицы остановок
function toggleStops(stopsTableId) {
    // Получение элемента таблицы остановок по его идентификатору
    const stopsTable = document.getElementById(stopsTableId);
    // Проверка текущего состояния отображения таблицы и переключение его
    if (stopsTable.style.display === "none") {
        // Если таблица скрыта, отображаем её
        stopsTable.style.display = "block";
    } else {
        // Если таблица отображена, скрываем её
        stopsTable.style.display = "none";
    }
}



// Функция для получения текста, описывающего количество остановок
function getStopCountText(count) {
    // Вложенная функция для определения правильного склонения слова "остановка"
    function getDeclension(num, nominative, genitiveSingular, genitivePlural) {
        // Если число оканчивается на 1, но не на 11, используем именительный падеж
        if (num % 10 === 1 && num % 100 !== 11) {
            return nominative;
        // Если число оканчивается на 2-4, но не на 12-14, используем родительный падеж единственного числа
        } else if (num % 10 >= 2 && num % 10 <= 4 && (num % 100 < 10 || num % 100 >= 20)) {
            return genitiveSingular;
        // В остальных случаях используем родительный падеж множественного числа
        } else {
            return genitivePlural;
        }
    }

    // Если количество остановок равно нулю, возвращаем соответствующий текст
    if (count === 0) {
        return "Без остановок";
    }

    // Определяем правильное склонение слова "остановка"
    let declension = getDeclension(count, "Остановка", "Остановки", "Остановок");
    // Возвращаем строку с количеством и правильным склонением
    return count + " " + declension;
}



function extractTransferCityName(segment) {
    const stops = segment["stops"];
    const transferStop = stops[0];
    const fullName = transferStop["name"];
    const cityNameMatch = fullName.match(/^[^\s]+/); // Регулярное выражение для извлечения первого слова до пробела
    return cityNameMatch ? cityNameMatch[0].toUpperCase() : fullName.toUpperCase(); // Возвращаем найденное имя города в верхнем регистре или полное имя в верхнем регистре, если не найдено
}



function createTransferRoute(routes, index, departureStation, arrivalStation) {
    let transferRouteHtml = '';  // Инициализация пустой строки для хранения HTML-кода
    const filteredRoutes = routes.filter(segment => segment.stops.length > 1);  // Фильтрация пустых и единичных сегментов

    // Проверка, что у нас есть хотя бы два сегмента
    if (filteredRoutes.length > 1) {
        let totalTravelTimeMs = 0;
        let totalPrice = 0;
        let totalLayoverTimeMs = 0;
        let transferStation;

        // Перебор отфильтрованных маршрутов и генерация HTML-кода для каждого сегмента
        filteredRoutes.forEach((segment, segmentIndex) => {
            transferRouteHtml += route(segment, `${index}-${segmentIndex}`);

            const departureDate = new Date(segment.stops[0].departureTime);
            const arrivalDate = new Date(segment.stops[segment.stops.length - 1].arrivalTime);
            const travelTimeMs = arrivalDate - departureDate;
            totalTravelTimeMs += travelTimeMs;
            totalPrice += segment.price;

            if (segmentIndex > 0) {
                const previousArrivalDate = new Date(filteredRoutes[segmentIndex - 1].stops[filteredRoutes[segmentIndex - 1].stops.length - 1].arrivalTime);
                const layoverTimeMs = departureDate - previousArrivalDate;
                totalLayoverTimeMs += layoverTimeMs;
            }
            transferStation = extractTransferCityName(segment);
        });

        // Общее время в пути (включая пересадочные)
        const totalTimeMs = totalTravelTimeMs + totalLayoverTimeMs;
        const totalMinutes = Math.floor(totalTimeMs / 60000);
        const totalHours = Math.floor(totalMinutes / 60);
        const remainingMinutes = totalMinutes % 60;

        // Форматирование итоговой цены
        const formattedTotalPrice = formatPrice(totalPrice);

        // Возвращение HTML-кода для пересадочного маршрута
        return `
            <div class="transfer-route-container">
                <table class="route-table">
                    <tr>
                        <th class='transfer-caption'>Пересадочный маршрут</th>
                    </tr>
                    <tr>
                        <td class='route-cell'>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <strong>${departureStation.toUpperCase()}</strong>
                                </div>
                                <div class="arrow">
                                    <svg width="150" height="20" viewBox="0 0 150 20" xmlns="http://www.w3.org/2000/svg">
                                    <line x1="0" y1="10" x2="140" y2="10" stroke="black" stroke-width="2"/>
                                    <polygon points="140,5 150,10 140,15" fill="black"/>
                                    </svg>
                                </div>
                                <div>
                                    <strong>${transferStation}</strong>
                                </div>
                                <div class="arrow">
                                    <svg width="150" height="20" viewBox="0 0 150 20" xmlns="http://www.w3.org/2000/svg">
                                    <line x1="0" y1="10" x2="140" y2="10" stroke="black" stroke-width="2"/>
                                    <polygon points="140,5 150,10 140,15" fill="black"/>
                                    </svg>
                                </div>
                                <div>
                                    <strong>${arrivalStation.toUpperCase()}</strong>
                                </div>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
                                <div>
                                    <strong>Общее время в пути</strong><br>
                                    ${totalHours}ч ${remainingMinutes}м
                                </div>
                                <div>
                                    <strong>Сумма стоимости билетов</strong><br>
                                    ₽${formattedTotalPrice}
                                </div>
                            </div>
                        </td>
                    </tr>
                </table>
                <div class="transfer-route-content">
                    ${transferRouteHtml}
                </div>
            </div>`;
    } else {
        // Возвращаем пустую строку, если нет пересадочных маршрутов или они не соответствуют условиям
        return '';
    }
}




async function send() {
    // Получение значений из полей ввода
    const departure_station = document.getElementById("from").value;
    const arrival_station = document.getElementById("to").value;
    const date = document.getElementById("date").value;

    try {
        // Отправка GET-запроса на сервер
        const response = await fetch(`/?departure_station=${departure_station}&arrival_station=${arrival_station}&date=${date}`);
        
        // Проверка успешности ответа
        if (response.ok) {
            // Парсинг ответа в формате JSON
            const data = await response.json();

            // Проверка, есть ли маршруты в ответе
            if (data.length === 0) {
                document.getElementById("get").innerHTML = `<div class="no-routes-message">Маршруты не найдены</div>`;
                return;
            }

            let directSegments = []; // Список для безпересадочных маршрутов
            const transferRoutes = []; // Список для пересадочных маршрутов

            // Перебор элементов данных
            data.forEach(item => {
                // Проверка наличия сегментов в элементе
                if (item.segments && item.segments.length > 0) {
                    // Если сегмент один, добавляем его в список безпересадочных маршрутов
                    if (item.segments.length === 1) {
                        directSegments.push(item.segments[0]);
                    } else {
                        // Иначе добавляем в список пересадочных маршрутов
                        transferRoutes.push(item.segments);
                    }
                }
            });

            // Удаление дубликатов в безпересадочных маршрутах
            directSegments = removeDuplicateDirectSegments(directSegments);

            // Сортировка безпересадочных маршрутов по времени отправления
            directSegments.sort((a, b) => getEarliestDeparture(a) - getEarliestDeparture(b));

            // Создание HTML-кода для безпересадочных маршрутов
            const directTables = directSegments.map((segment, index) => route(segment, index)).join("");
            // Создание HTML-кода для пересадочных маршрутов
            const transferTables = transferRoutes.map((segments, index) => createTransferRoute(segments, index, departure_station, arrival_station)).join("");

            // Обновление содержимого

            document.getElementById("get").innerHTML = directTables + transferTables;

            // Добавление обработчиков событий для кнопок остановок
            document.querySelectorAll(".stop-button").forEach(button => {
                button.addEventListener("mouseover", function() {
                    this.style.backgroundColor = "#567d7d";
                });

                button.addEventListener("mouseout", function() {
                    this.style.backgroundColor = "#3f5e5e";
                });
            });
        } else if (response.status === 500) {
            // Обработка ошибки сервера
            const errorData = await response.json();
            document.getElementById("get").innerHTML = `<div class="error-message">${errorData.error}</div>`;
        } else {
            // Обработка прочих ошибок
            console.error('Ошибка сервера:', response);
            document.getElementById("get").innerHTML = `<div class="no-routes-message">Ошиб-о-о-о-чка</div>`;
        }
    } catch (error) {
        // Обработка сетевой ошибки
        console.error('Ошибка сети:', error);
        document.getElementById("get").innerHTML = `<div class="no-routes-message">Проверьте введенные данные.</div>`;
    }
}



// Функция для удаления дубликатов в безпересадочных маршрутах
function removeDuplicateDirectSegments(directSegments) {
    // Создание объекта для хранения уникальных сегментов
    const uniqueSegments = {};

    // Перебор всех сегментов
    directSegments.forEach(segment => {
        // Используем номер рейса в качестве ключа
        const key = segment.voyage_number;

        // Если сегмента с таким ключом еще нет или у текущего сегмента цена ниже, обновляем объект
        if (!uniqueSegments[key] || segment.price < uniqueSegments[key].price) {
            uniqueSegments[key] = segment;
        }
    });

    // Возвращаем значения объекта, которые представляют собой уникальные сегменты
    return Object.values(uniqueSegments);
}
