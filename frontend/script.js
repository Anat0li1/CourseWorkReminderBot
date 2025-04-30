const reminderCount = document.getElementById('reminderCount');
        const remindersContainer = document.getElementById('remindersContainer');
        const remindEndCheckbox = document.getElementById('remindEndCheckbox');
        const remindEndContainer = document.getElementById('remindEndContainer');
        const repeatType = document.getElementById('repeatType');
        const customRepeatFields = document.getElementById('customRepeatFields');

        function renderReminders() {
            remindersContainer.innerHTML = '';
            const count = parseInt(reminderCount.value);
            for (let i = 0; i < count; i++) {
                const div = document.createElement('div');
                div.className = 'reminder-item';
                div.innerHTML = `
                    <input type="number" min="1" class="remind-before" placeholder="За">
                    <select class="remind-indicator">
                        <option value="1">Хвилина</option>
                        <option value="2">Година</option>
                        <option value="3">День</option>
                        <option value="4">Тиждень</option>
                        <option value="5">Місяць</option>
                        <option value="6">Рік</option>
                    </select>
                `;
                remindersContainer.appendChild(div);
            }
        }

        reminderCount.addEventListener('change', renderReminders);
        remindEndCheckbox.addEventListener('change', () => {
            remindEndContainer.classList.toggle('hidden', !remindEndCheckbox.checked);
        });

        repeatType.addEventListener('change', () => {
            customRepeatFields.classList.toggle('hidden', repeatType.value !== '7');
        });

        document.getElementById('eventForm').addEventListener('submit', async (e) => {
            e.preventDefault();

            const reminders = Array.from(document.querySelectorAll('.reminder-item'))
                .slice(0, parseInt(reminderCount.value))
                .map(item => ({
                    before: parseInt(item.querySelector('.remind-before').value),
                    indicator: parseInt(item.querySelector('.remind-indicator').value)
                }));

            const payload = {
                name: document.getElementById('name').value,
                description: document.getElementById('description').value,
                start: document.getElementById('start').value,
                end: document.getElementById('end').value,
                repeat: {
                    type: parseInt(repeatType.value),
                    start: document.getElementById('startRepeat').value,
                    duration: parseInt(document.getElementById('repeatDuration').value),
                    indicator: parseInt(document.getElementById('repeatIndicator').value),
                    end: document.getElementById('endRepeat').value
                },
                reminders,
                remindEnd: remindEndCheckbox.checked ? {
                    before: parseInt(document.getElementById('remindEndBefore').value),
                    indicator: parseInt(document.getElementById('remindEndIndicator').value)
                } : null
            };

            try {
                const response = await fetch('/save_event', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (response.ok) {
                    alert('Подію збережено!');
                } else {
                    alert('Помилка при збереженні!');
                }
            } catch (error) {
                console.error('Error saving event:', error);
                alert('Сталася помилка при відправленні запиту.');
            }
        });

        renderReminders();