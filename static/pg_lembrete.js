document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('#reminder-form');
  const alarmAudio = document.querySelector('#alarme');
  const customAlert = document.querySelector('#custom-alert');
  const alertMessage = document.querySelector('#alert-message');
  const alertOkButton = document.querySelector('#alert-ok');
  const lembretesList = document.querySelector('#lembretes-list');

  // Função para agendar o alarme
  function scheduleAlarm(name, dateStr, timeStr) {
    const reminderDateTime = new Date(`${dateStr}T${timeStr}:00`);
    const now = new Date();
    const timeDifference = reminderDateTime - now;

    if (timeDifference > 0) {
      setTimeout(() => {
        alarmAudio.play();
        alertMessage.textContent = `🔔 Lembrete: ${name}\nÉ hora de bater o ponto!`;
        customAlert.style.display = 'block';
      }, timeDifference);
    }
  }

  // Agendar alarmes de todos os lembretes existentes ao carregar a página
  document.querySelectorAll('#lembretes-list li').forEach(li => {
    scheduleAlarm(li.textContent.split(' - ')[0], li.dataset.date, li.dataset.time);
  });

  // Submissão do formulário sem recarregar
  form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const formData = new FormData(form);
    const name = formData.get('name');
    const date = formData.get('data');
    const time = formData.get('hora');

    if (!name || !date || !time) return alert("Preencha todos os campos.");

    try {
      const response = await fetch(form.action, {
        method: 'POST',
        body: formData
      });

      if (response.redirected) {
        // Não recarrega a página
        const li = document.createElement('li');
        li.textContent = `${name} - ${date} ${time}`;
        li.dataset.date = date;
        li.dataset.time = time;
        lembretesList.appendChild(li);

        scheduleAlarm(name, date, time);
        form.reset();
      }
    } catch (err) {
      console.error('Erro ao salvar lembrete:', err);
    }
  });

  alertOkButton.addEventListener('click', () => {
    customAlert.style.display = 'none';
  });
});
