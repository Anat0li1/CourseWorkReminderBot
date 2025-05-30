  const repeatType = document.getElementById('repeatType');
  const customRepeatFields = document.getElementById('customRepeatFields');
  const reminderCount = document.getElementById('reminderCount');
  const remindersContainer = document.getElementById('remindersContainer');
  const remindEndCheckbox = document.getElementById('remindEndCheckbox');
  const remindEndContainer = document.getElementById('remindEndContainer');
  const initDataUnsafe = window.Telegram.WebApp.initData;
  const userData = window.Telegram.WebApp.initDataUnsafe?.user;


  repeatType.addEventListener('change', () => {
    customRepeatFields.classList.toggle('hidden', repeatType.value !== '7');
  });

  reminderCount.addEventListener('change', updateRemindersToggle);

  remindEndCheckbox.addEventListener('change', () => {
    remindEndContainer.classList.toggle('hidden', !remindEndCheckbox.checked);
  });

function updateRemindersToggle() {
  console.log("q");
    remindersContainer.innerHTML = '';
    const count = parseInt(reminderCount.value);
    for (let i = 0; i < count; i++) {
      const reminderDiv = document.createElement('div');
      reminderDiv.className = 'reminder-item';
      reminderDiv.innerHTML = `
        <input type="number" min="1" max="50" name="remind_before_${i}" class="remind-before">
        <select name="remind_indicator_${i}" class="remind-indicator">
          <option value="1">Хвилина</option>
          <option value="2">Година</option>
          <option value="3">День</option>
          <option value="4">Тиждень</option>
          <option value="5">Місяць</option>
          <option value="6">Рік</option>
        </select>
      `;
      remindersContainer.appendChild(reminderDiv);
    }
}

function getEventIdFromUrl() {
  const pathSegments = window.location.pathname.split("/");
  const eventIndex = pathSegments.indexOf("miniapp") + 2;
  return pathSegments[eventIndex] || null;
}

document.addEventListener("DOMContentLoaded", async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const eventId = getEventIdFromUrl();
  const submitButton = document.getElementById('submitButton');
  updateRemindersToggle();
  console.log(eventId)
  if (eventId) {
      await loadEventData(eventId);
      submitButton.textContent = "Оновити подію";
      submitButton.setAttribute("data-mode", "edit"); 
      submitButton.setAttribute("data-event-id", eventId);
  } else {
      submitButton.textContent = "Зберегти подію";
      submitButton.setAttribute("data-mode", "create"); 
  }
});

document.getElementById('eventForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();

  const submitButton = document.getElementById('submitButton');
  const mode = submitButton.getAttribute("data-mode");
  const eventId = submitButton.getAttribute("data-event-id");
  
  const payload = collectFormData();

  let url = "/save_all"; 
  if (mode === "edit" && eventId) {
      url = `/update_event/${eventId}`; 
  }

  try {
      const response = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
      });

      const data = await response.json();
      if (response.ok) {
          alert(mode === "edit" ? "Подію оновлено!" : "Подію збережено!");
      } else {
          alert(`${data.status}: ${data.type} - ${data.message}`);
      }
  } catch (error) {
      console.error('Error saving event:', error);
      alert('Сталася помилка при відправленні запиту.');
  }
});

function collectFormData() {
  const count = parseInt(document.getElementById('reminderCount')?.value ?? '0');
  const reminderElements = Array.from(document.querySelectorAll('.reminder-item'));
  const reminders = reminderElements.slice(0, count).map((item, i) => {
  const beforeEl = document.querySelector(`input[name='remind_before_${i}']`);
  const indicatorEl = document.querySelector(`select[name='remind_indicator_${i}']`);
  return {
    before: beforeEl ? parseInt(beforeEl.value || '0') : 0,
    indicator: indicatorEl ? parseInt(indicatorEl.value || '0') : 0
  };
});
  return {
      userId: 1081733675,
      name: document.getElementById('name')?.value ?? '',
      description: document.getElementById('description')?.value ?? '',
      start: document.getElementById('start')?.value ?? '',
      end: document.getElementById('end')?.value ?? '',
      repeat: {
          type: parseInt(document.getElementById('repeatType')?.value ?? '-1'),
          start: document.getElementById('startRepeat')?.value ?? '',
          duration: parseInt(document.getElementById('repeatDuration')?.value ?? '0'),
          indicator: parseInt(document.getElementById('repeatIndicator')?.value ?? '-1'),
          end: document.getElementById('endRepeat')?.value ?? ''
      },
      reminders,
      remindEnd: document.getElementById('remindEndCheckbox')?.checked ? {
          before: parseInt(document.getElementById('remindEndBefore')?.value ?? '0'),
          indicator: parseInt(document.getElementById('remindEndIndicator')?.value ?? '0')
      } : null
  };
}

// document.getElementById('eventForm')?.addEventListener('submit', async (e) => {
//   e.preventDefault();

//   const reminderElements = Array.from(document.querySelectorAll('.reminder-item'));
//   const count = parseInt(document.getElementById('reminderCount')?.value ?? '0');

//   const reminders = reminderElements.slice(0, count).map((item, i) => {
//     const beforeEl = document.querySelector(`input[name='remind_before_${i}']`);
//     console.log('beforeEl', beforeEl);
//     console.log('value', beforeEl.value);
//     const indicatorEl = document.querySelector(`select[name='remind_indicator_${i}']`);
//     console.log('indicatorEl', indicatorEl);
//     console.log('value', indicatorEl.value);
//     return {
//       before: beforeEl ? parseInt(beforeEl.value || '0') : 0,
//       indicator: indicatorEl ? parseInt(indicatorEl.value || '0') : 0
//     };
//   });

//   const payload = {
//     userId: userData?.id,
//     name: document.getElementById('name')?.value ?? '',
//     description: document.getElementById('description')?.value ?? '',
//     start: document.getElementById('start')?.value ?? '',
//     end: document.getElementById('end')?.value ?? '',
//     repeat: {
//       type: parseInt(document.getElementById('repeatType')?.value ?? '-1'),
//       start: document.getElementById('startRepeat')?.value ?? '',
//       duration: parseInt(document.getElementById('repeatDuration')?.value ?? '0'),
//       indicator: parseInt(document.getElementById('repeatIndicator')?.value ?? '-1'),
//       end: document.getElementById('endRepeat')?.value ?? ''
//     },
//     reminders,
//     remindEnd: document.getElementById('remindEndCheckbox')?.checked ? {
//       before: parseInt(document.getElementById('remindEndBefore')?.value ?? '0'),
//       indicator: parseInt(document.getElementById('remindEndIndicator')?.value ?? '0')
//     } : null
//   };

//   try {
//     const response = await fetch('/save_all', {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify(payload)
//     });
//     const data = await response.json(); 
//     if (response.ok) {
//       alert('Подію збережено!');
//     } else {
//       alert(`${data.status}: ${data.type} - ${data.message}`);
//     }
//   } catch (error) {
//     console.error('Error saving event:', error);
//     alert('Сталася помилка при відправленні запиту.');
//   }
// });

updateRemindersToggle();

function convertToLocalTime(utcDate) {
  const localDate = new Date(utcDate);
  const timezoneOffsetMinutes = localDate.getTimezoneOffset();
  localDate.setMinutes(localDate.getMinutes() - timezoneOffsetMinutes);
  const year = localDate.getFullYear();
  const month = String(localDate.getMonth() + 1).padStart(2, '0');
  const day = String(localDate.getDate()).padStart(2, '0');
  const hours = String(localDate.getHours()).padStart(2, '0');
  const minutes = String(localDate.getMinutes()).padStart(2, '0');

  return `${year}-${month}-${day}T${hours}:${minutes}`;
}



async function loadEventData(eventId) {
  try {
    const response = await fetch(`/api/get_event/${eventId}`);
    
      const data = await response.json();
      console.log(data)
      document.getElementById('name').value = data.name;
      document.getElementById('description').value = data.description;
      document.getElementById('start').value = convertToLocalTime(data.start_time);
      document.getElementById('end').value = convertToLocalTime(data.end_time);
      document.getElementById('repeatType').value = data.repeat.type;
      
      customRepeatFields.classList.toggle('hidden', data.repeat.type !== 7);
      if (data.repeat.type === 7) {
          document.getElementById('startRepeat').value = data.repeat.start ?? '';
          document.getElementById('repeatDuration').value = data.repeat.duration ?? '';
          document.getElementById('repeatIndicator').value = data.repeat.indicator ?? '';
          document.getElementById('endRepeat').value = data.repeat.end ?? '';
      }

      updateReminders(data.reminders);

      if (data.remindEnd) {
          remindEndCheckbox.checked = true;
          remindEndContainer.classList.remove('hidden');
          document.getElementById('remindEndBefore').value = data.remindEnd.before;
          document.getElementById('remindEndIndicator').value = data.remindEnd.indicator;
      }

  } catch (error) {
      console.error("Помилка завантаження події:", error);
  }
}

function updateReminders(remindersData) {
  remindersContainer.innerHTML = '';
  
  if (remindersData.length > 0) {
      reminderCount.value = remindersData.length;
  }

  remindersData.forEach((reminder, i) => {
      const reminderDiv = document.createElement('div');
      reminderDiv.className = 'reminder-item';
      reminderDiv.innerHTML = `
          <input type="number" min="1" max="50" name="remind_before_${i}" class="remind-before" value="${reminder.before}">
          <select name="remind_indicator_${i}" class="remind-indicator">
              <option value="1" ${reminder.indicator === 1 ? 'selected' : ''}>Хвилина</option>
              <option value="2" ${reminder.indicator === 2 ? 'selected' : ''}>Година</option>
              <option value="3" ${reminder.indicator === 3 ? 'selected' : ''}>День</option>
              <option value="4" ${reminder.indicator === 4 ? 'selected' : ''}>Тиждень</option>
              <option value="5" ${reminder.indicator === 5 ? 'selected' : ''}>Місяць</option>
              <option value="6" ${reminder.indicator === 6 ? 'selected' : ''}>Рік</option>
          </select>
      `;
      remindersContainer.appendChild(reminderDiv);
  });
}