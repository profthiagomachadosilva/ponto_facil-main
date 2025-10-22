document.getElementById('justificativaForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const form = e.target;
            const submitBtn = form.querySelector('.submit-btn');
            const messageDiv = document.getElementById('message');
            
            // Get form data
            const nome = document.getElementById('nome').value.trim();
            const data = document.getElementById('data').value;
            const motivo = document.getElementById('motivo').value.trim();
            
            
            // Validate form
            if (!nome || !data || !motivo) {
                showMessage('Todos os campos são obrigatórios.', 'error');
                return;
            }
            
            // Convert date format from yyyy-mm-dd to dd/mm/yyyy
            const dateObj = new Date(data);
            const formattedDate = `${String(dateObj.getDate()).padStart(2, '0')}/${String(dateObj.getMonth() + 1).padStart(2, '0')}/${dateObj.getFullYear()}`;
            
            // Show loading state
            submitBtn.textContent = 'Enviando...';
            form.classList.add('loading');
            
            try {
                const response = await fetch('/justificativas', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        nome_funcionario: nome,
                        data_nao_registrada: formattedDate,
                        motivo: motivo
                    })
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    showMessage(result.message, 'success');
                    form.reset();
                } else {
                    showMessage(result.error || 'Erro ao enviar justificativa.', 'error');
                }
            } catch (error) {
                showMessage('Erro de conexão. Tente novamente.', 'error');
            } finally {
                // Reset loading state
                submitBtn.textContent = 'Enviar Justificativa';
                form.classList.remove('loading');
            }
        });
        
        function showMessage(text, type) {
            const messageDiv = document.getElementById('message');
            messageDiv.textContent = text;
            messageDiv.className = `message ${type}`;
            messageDiv.classList.remove('hidden');
            
            // Hide message after 5 seconds
            setTimeout(() => {
                messageDiv.classList.add('hidden');
            }, 5000);
        }