// Database de usuários (em produção, isso ficaria no servidor)
const users = {
  programacao: { password: "python2024", role: "student", name: "Fulano de Tal" },
  professor: { password: "scratch123", role: "teacher", name: "Prof. Silva" },
  aluno1: { password: "aula2024", role: "student", name: "Maria Santos" },
  aluno2: { password: "scratch456", role: "student", name: "João Oliveira" },
  admin: { password: "admin123", role: "admin", name: "Administrador" },
}

// Função para adicionar novo usuário
function addUser(username, password, role = "student", name = "") {
  users[username] = { password, role, name }
  localStorage.setItem("users", JSON.stringify(users))
  console.log(`Usuário ${username} adicionado com sucesso!`)
}

// Carregar usuários salvos do localStorage
function loadUsers() {
  const savedUsers = localStorage.getItem("users")
  if (savedUsers) {
    Object.assign(users, JSON.parse(savedUsers))
  }
}

// Lógica de Login e Ambiente (já existente)
document.addEventListener("DOMContentLoaded", () => {
  loadUsers() // Carrega usuários salvos

  const loginForm = document.getElementById("loginForm")

  if (loginForm) {
    loginForm.addEventListener("submit", (e) => {
      e.preventDefault()

      const username = document.getElementById("username").value
      const password = document.getElementById("password").value

      // Verificar se usuário existe e senha está correta
      if (users[username] && users[username].password === password) {
        localStorage.setItem("isLoggedIn", "true")
        localStorage.setItem("username", username)
        localStorage.setItem("userRole", users[username].role)
        localStorage.setItem("userName", users[username].name)

        // Redirecionar baseado no papel do usuário
        if (users[username].role === "teacher" || users[username].role === "admin") {
          window.location.href = "teacher-dashboard.html" // Dashboard do professor
        } else {
          window.location.href = "dashboard.html"
        }
      } else {
        alert("Usuário ou senha incorretos!")
      }
    })
  }

  // Check if user is logged in
  const isLoginPage = window.location.pathname.endsWith("index.html") || window.location.pathname === "/";

  if (!isLoginPage && !localStorage.getItem("isLoggedIn")) {
    window.location.href = "index.html";
  }

    // --- Função para buscar e exibir os alunos do backend (já existente) ---
    function fetchAlunosFromBackend() {
        fetch('http://127.0.0.1:5000/alunos') // A URL da sua API Flask
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erro HTTP! Status: ${response.status}`);
                }
                return response.json(); // Converte a resposta para JSON
            })
            .then(alunos => {
                console.log('Alunos carregados do backend:', alunos);
                displayAlunosInInfoTable(alunos); // Chame a função para renderizar na tabela específica
            })
            .catch(error => {
                console.error('Erro ao buscar alunos do backend:', error);
                // Opcional: Exibir uma mensagem de erro na interface do usuário
            });
    }

    // --- Função para popular a tabela de info_alunos em database.html (MODIFICADA) ---
    function displayAlunosInInfoTable(alunos) {
        const tbody = document.querySelector('#table_info_alunos tbody');
        
        if (!tbody) {
            console.warn('Elemento tbody da tabela de info_alunos não encontrado. Verifique database.html.');
            return;
        }

        tbody.innerHTML = ''; // Limpa as linhas estáticas existentes

        if (alunos.length === 0) {
            const noDataRow = document.createElement('tr');
            noDataRow.innerHTML = `<td colspan="12" style="text-align: center;">Nenhum aluno encontrado.</td>`; 
            tbody.appendChild(noDataRow);
            return;
        }

        alunos.forEach(aluno => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${aluno.turma || ''}</td>
                <td>${aluno.nome || ''}</td>
                <td>${aluno.email || ''}</td>
                <td>${aluno.telefone || ''}</td>
                <td>${aluno.data_nascimento || ''}</td>
                <td>${aluno.rg || ''}</td>
                <td>${aluno.cpf || ''}</td>
                <td>${aluno.endereco || ''}</td>
                <td>${aluno.escolaridade || ''}</td>
                <td>${aluno.escola || ''}</td>
                <td>${aluno.responsavel || ''}</td>
                <td>
                    <button class="action-btn small" onclick="editAluno(${aluno.id})" title="Editar">✏️</button>
                    <button class="action-btn small danger" onclick="deleteAluno(${aluno.id})" title="Excluir">🗑️</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    // --- Chamada inicial para carregar os alunos (já existente) ---
    if (window.location.pathname.endsWith('database.html')) {
        fetchAlunosFromBackend();
    }


    // --- LÓGICA PARA ADICIONAR ALUNO (já existente) ---
    window.addRecord = function() {
        const selectedTable = document.getElementById('tableSelect').value;
        if (selectedTable === 'info_alunos') {
            document.getElementById('addAlunoModal').classList.remove('hidden');
        } else {
            alert(`Funcionalidade de adicionar ainda não implementada para a tabela: ${selectedTable}`);
        }
    }
    
    window.closeAddAlunoModal = function() {
        document.getElementById('addAlunoModal').classList.add('hidden');
        document.getElementById('addAlunoForm').reset(); // Limpa o formulário
    }

    const addAlunoForm = document.getElementById('addAlunoForm');
    if (addAlunoForm) {
        addAlunoForm.addEventListener('submit', function(event) {
            event.preventDefault();

            const formData = new FormData(addAlunoForm);
            const alunoData = {};
            for (let [key, value] of formData.entries()) {
                if (key === 'data_nascimento' && value) {
                    alunoData[key] = value;
                } else {
                    alunoData[key] = value;
                }
            }
            console.log('Dados do novo aluno a serem enviados:', alunoData);
            sendAlunoToBackend(alunoData);
        });
    }

    function sendAlunoToBackend(alunoData) {
        fetch('http://127.0.0.1:5000/alunos/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(alunoData),
        })
        .then(response => response.json())
        .then(data => {
            console.log('Resposta do backend:', data);
            if (data.success) {
                alert('Aluno adicionado com sucesso!');
                closeAddAlunoModal();
                fetchAlunosFromBackend(); // Recarrega a tabela
            } else {
                alert('Erro ao adicionar aluno: ' + (data.message || 'Erro desconhecido.'));
            }
        })
        .catch(error => {
            console.error('Erro de rede ou servidor ao enviar aluno:', error);
            alert('Erro de conexão ou servidor ao tentar adicionar aluno. Verifique o console.');
        });
    }


    // --- LÓGICA PARA DELETAR ALUNO (já existente) ---
    window.deleteAluno = function(alunoId) {
        if (confirm(`Tem certeza que deseja excluir o aluno com ID ${alunoId}?`)) {
            fetch(`http://127.0.0.1:5000/alunos/delete/${alunoId}`, {
                method: 'DELETE',
            })
            .then(response => response.json())
            .then(data => {
                console.log('Resposta do backend (delete):', data);
                if (data.success) {
                    alert('Aluno excluído com sucesso!');
                    fetchAlunosFromBackend(); // Recarrega a tabela
                } else {
                    alert('Erro ao excluir aluno: ' + (data.message || 'Erro desconhecido.'));
                }
            })
            .catch(error => {
                console.error('Erro de rede ou servidor ao excluir aluno:', error);
                alert('Erro de conexão ou servidor ao tentar excluir aluno.');
            });
        }
    };


    // --- LÓGICA PARA EDITAR ALUNO (COMPLETA AGORA) ---

    // Função para abrir o modal de edição e preencher com os dados do aluno (já existente)
    window.editAluno = function(alunoId) {
        fetch(`http://127.0.0.1:5000/alunos/${alunoId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erro HTTP! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(aluno => {
                if (aluno) {
                    document.getElementById('editAlunoId').value = aluno.id;
                    document.getElementById('editTurma').value = aluno.turma || '';
                    document.getElementById('editNome').value = aluno.nome || '';
                    document.getElementById('editEmail').value = aluno.email || '';
                    document.getElementById('editTelefone').value = aluno.telefone || '';
                    document.getElementById('editDataNascimento').value = aluno.data_nascimento || '';
                    document.getElementById('editRg').value = aluno.rg || '';
                    document.getElementById('editCpf').value = aluno.cpf || '';
                    document.getElementById('editEndereco').value = aluno.endereco || '';
                    document.getElementById('editEscolaridade').value = aluno.escolaridade || '';
                    document.getElementById('editEscola').value = aluno.escola || '';
                    document.getElementById('editResponsavel').value = aluno.responsavel || '';

                    document.getElementById('editAlunoModal').classList.remove('hidden');
                } else {
                    alert('Aluno não encontrado para edição.');
                }
            })
            .catch(error => {
                console.error('Erro ao buscar dados do aluno para edição:', error);
                alert('Erro ao carregar dados do aluno para edição.');
            });
    };

    // Função para fechar o modal de edição (já existente)
    window.closeEditAlunoModal = function() {
        document.getElementById('editAlunoModal').classList.add('hidden');
        document.getElementById('editAlunoForm').reset();
    };

    // Lógica para enviar o formulário de edição (AGORA ATIVADA)
    const editAlunoForm = document.getElementById('editAlunoForm');
    if (editAlunoForm) {
        editAlunoForm.addEventListener('submit', function(event) {
            event.preventDefault();

            const formData = new FormData(editAlunoForm);
            const alunoData = {};
            for (let [key, value] of formData.entries()) {
                // Formate a data de nascimento se for o caso
                if (key === 'data_nascimento' && value) {
                    // O input type="date" já retorna "YYYY-MM-DD", que é o formato necessário para MySQL DATE
                    alunoData[key] = value;
                } else {
                    alunoData[key] = value;
                }
            }

            const alunoId = alunoData.id; // Pega o ID do aluno do campo oculto
            delete alunoData.id; // Remove o ID do objeto de dados, pois ele vai na URL da API

            console.log('Dados do aluno a serem atualizados:', alunoData, 'ID:', alunoId);

            // Chame a função para enviar os dados editados para o backend
            sendEditedAlunoToBackend(alunoId, alunoData);
        });
    }

    // FUNÇÃO sendEditedAlunoToBackend (COMPLETA AGORA)
    function sendEditedAlunoToBackend(alunoId, alunoData) {
        fetch(`http://127.0.0.1:5000/alunos/edit/${alunoId}`, { // A URL do seu endpoint Flask (método PUT)
            method: 'PUT', // Método HTTP PUT para atualização
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(alunoData), // Converte o objeto JavaScript em uma string JSON
        })
        .then(response => response.json()) // Espera uma resposta JSON do backend
        .then(data => {
            console.log('Resposta do backend (edição):', data);
            if (data.success) {
                alert('Aluno atualizado com sucesso!');
                closeEditAlunoModal(); // Fecha o modal
                fetchAlunosFromBackend(); // Recarrega a tabela para mostrar o aluno atualizado
            } else {
                alert('Erro ao atualizar aluno: ' + (data.message || 'Erro desconhecido.'));
            }
        })
        .catch(error => {
            console.error('Erro de rede ou servidor ao atualizar aluno:', error);
            alert('Erro de conexão ou servidor ao tentar atualizar aluno. Verifique o console.');
        });
    }


    // --- Outras Funções (já existentes) ---
    // Funções de navegação e logout
    function goBack() {
        window.history.back();
    }

    function goToPage(page) {
        window.location.href = page;
    }

    function logout() {
      localStorage.removeItem("isLoggedIn")
      localStorage.removeItem("username")
      localStorage.removeItem("userRole")
      localStorage.removeItem("userName")
      window.location.href = "index.html"
    }

    const userAvatar = document.querySelector(".user-avatar")
    if (userAvatar) {
      console.log('Elemento .user-avatar encontrado:', userAvatar);
      userAvatar.addEventListener("click", () => {
        console.log('Clique no .user-avatar detectado.');
        if (confirm("Deseja fazer logout?")) {
          console.log('Confirmação de logout aceita. Chamando logout().');
          logout()
        } else {
          console.log('Confirmação de logout cancelada.');
        }
      })
      userAvatar.style.cursor = "pointer"
      userAvatar.title = "Clique para fazer logout"
    } else {
      console.warn('Elemento .user-avatar NÃO ENCONTRADO.');
    }

    function abrirWhatsApp() {
        const whatsappLink = "https://chat.whatsapp.com/GHZuEpQhb5uGFROPWioy9o?mode=ac_c";
        window.open(whatsappLink, '_blank');
    }
});

// Funções globais para serem acessíveis diretamente do HTML (onclick)
window.changeTable = function() {
    const selectedTable = document.getElementById('tableSelect').value;
    document.querySelectorAll('.database-table-container').forEach(table => {
        table.classList.add('hidden');
    });
    document.getElementById(`table_${selectedTable}`).classList.remove('hidden');
    // Se a tabela selecionada for 'info_alunos', recarregue os dados
    if (selectedTable === 'info_alunos') {
        // fetchAlunosFromBackend(); // Descomente e defina globalmente se precisar que mude de tabela e recarregue
    }
};

window.searchTable = function() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const activeTable = document.querySelector('.database-table-container:not(.hidden)');
    if (activeTable) {
        const rows = activeTable.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            if (text.includes(searchTerm)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }
};

window.editRecord = function() {
    const selectedTable = document.getElementById('tableSelect').value;
    if (selectedTable === 'info_alunos') {
        alert('Clique nos botões "✏️" ao lado de cada aluno para editar.');
    } else {
        alert(`Funcionalidade de edição ainda não implementada para a tabela: ${selectedTable}`);
    }
};