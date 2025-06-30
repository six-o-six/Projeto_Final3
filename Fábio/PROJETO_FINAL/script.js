// REMOÇÃO: A base de dados de usuários e a função addUser hardcoded não são mais necessárias, pois serão gerenciadas pelo backend.
// const users = {
//   programacao: { password: "python2024", role: "student", name: "Fulano de Tal" },
//   professor: { password: "scratch123", role: "teacher", name: "Prof. Silva" },
//   aluno1: { password: "aula2024", role: "student", name: "Maria Santos" },
//   aluno2: { password: "scratch456", role: "student", name: "João Oliveira" },
//   admin: { password: "admin123", role: "admin", name: "Administrador" },
// }
// function addUser(username, password, role = "student", name = "") {
//   users[username] = { password, role, name }
//   localStorage.setItem("users", JSON.stringify(users))
//   console.log(`Usuário ${username} adicionado com sucesso!`)
// }
// function loadUsers() {
//   const savedUsers = localStorage.getItem("users")
//   if (savedUsers) {
//     Object.assign(users, JSON.parse(savedUsers))
//   }
// }

document.addEventListener("DOMContentLoaded", () => {
  // REMOÇÃO: loadUsers() não é mais necessário aqui, pois o login será via API.
  // loadUsers()

  const loginForm = document.getElementById("loginForm");

  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => { // MODIFICAÇÃO: Adicionado 'async'
      e.preventDefault();

      const username = document.getElementById("username").value;
      const password = document.getElementById("password").value;

      try {
        // ADIÇÃO: Requisição para o endpoint de login do backend
        const response = await fetch('http://127.0.0.1:5000/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ username, password }),
        });

        const data = await response.json();

        if (data.success) {
            // ... (mantém o armazenamento no localStorage)
            localStorage.setItem("userRole", data.user.role); // Isso já pegará 'teacher' para ex-admins

            // Redirecionar baseado no papel do usuário
            // MODIFICAÇÃO: Simplifica a condição para apenas 'teacher'
            if (data.user.role === "teacher") {
                window.location.href = "teacher-dashboard.html";
            } else {
                window.location.href = "dashboard.html";
            }
        } else {
          alert('Erro no login: ' + data.message);
        }
      } catch (error) {
        console.error('Erro de rede ou servidor ao tentar logar:', error);
        alert('Erro de conexão ou servidor. Tente novamente mais tarde.');
      }
    });
  }

  // Check if user is logged in
  const isLoginPage = window.location.pathname.endsWith("index.html") || window.location.pathname === "/";

    if (!isLoginPage && !localStorage.getItem("isLoggedIn")) {
        window.location.href = "index.html";
    }

  // ADIÇÃO: Lógica para mostrar/esconder o link de administração
    const userRole = localStorage.getItem("userRole"); // Pega o papel do usuário logado
    const adminLink = document.getElementById('adminLink');
    if (adminLink) { // Verifica se o elemento existe na página atual (no caso, teacher-dashboard.html)
        if (userRole === 'teacher') { // Agora, apenas professores (incluindo ex-admins) veem o link
            adminLink.style.display = 'block'; // Ou 'list-item', dependendo do seu CSS
        } else {
            adminLink.style.display = 'none';
        }
    }

  // --- Funções para buscar e exibir os alunos do backend (info_alunos) ---
  window.fetchAlunosFromBackend = async function() { // MODIFICAÇÃO: Tornada global e async
      try {
          const response = await fetch('http://127.0.0.1:5000/alunos');
          if (!response.ok) {
              throw new Error(`Erro HTTP! Status: ${response.status}`);
          }
          const alunos = await response.json();
          console.log('Alunos carregados do backend:', alunos);
          displayAlunosInInfoTable(alunos);
      } catch (error) {
          console.error('Erro ao buscar alunos do backend:', error);
          const tbody = document.querySelector('#table_info_alunos tbody');
          if (tbody) {
              tbody.innerHTML = `<tr><td colspan="12" style="text-align: center; color: red;">Erro ao carregar dados dos alunos.</td></tr>`;
          }
      }
  }

  // --- Função para popular a tabela de info_alunos em database.html ---
  function displayAlunosInInfoTable(alunos) {
      const tbody = document.querySelector('#table_info_alunos tbody');
      
      if (!tbody) {
          console.warn('Elemento tbody da tabela de info_alunos não encontrado. Verifique database.html.');
          return;
      }

      tbody.innerHTML = ''; // Limpa as linhas existentes

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

  // ADIÇÃO: Funções para buscar e exibir o status geral dos alunos (student_overall_status)
  window.fetchStudentOverallStatusFromBackend = async function() {
      try {
          const response = await fetch('http://127.0.0.1:5000/student_status');
          if (!response.ok) {
              throw new Error(`Erro HTTP! Status: ${response.status}`);
          }
          const statuses = await response.json();
          console.log('Status dos alunos carregados do backend:', statuses);
          displayStudentOverallStatusTable(statuses);
      } catch (error) {
          console.error('Erro ao buscar status dos alunos do backend:', error);
          const tbody = document.querySelector('#table_status_alunos tbody');
          if (tbody) {
              tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: red;">Erro ao carregar status dos alunos.</td></tr>`;
          }
      }
  }

  function displayStudentOverallStatusTable(statuses) {
      const tbody = document.querySelector('#table_status_alunos tbody');
      if (!tbody) {
          console.warn('Elemento tbody da tabela de status_alunos não encontrado.');
          return;
      }
      tbody.innerHTML = '';
      if (statuses.length === 0) {
          tbody.innerHTML = `<tr><td colspan="5" style="text-align: center;">Nenhum status de aluno encontrado.</td></tr>`;
          return;
      }

      statuses.forEach(status => {
          const row = document.createElement('tr');
          row.innerHTML = `
              <td>${status.student_name || ''}</td>
              <td>${status.current_status || ''}</td>
              <td>${status.presence_percentage !== null ? status.presence_percentage + '%' : ''}</td>
              <td>${status.activities_submitted_info || ''}</td>
              <td>${status.last_activity_completed || ''}</td>
          `;
          tbody.appendChild(row);
      });
  }

  // ADIÇÃO: Funções para buscar e exibir os dados de login dos usuários (users)
  window.fetchLoginAlunosFromBackend = async function() {
      try {
          const response = await fetch('http://127.0.0.1:5000/users');
          if (!response.ok) {
              throw new Error(`Erro HTTP! Status: ${response.status}`);
          }
          const users = await response.json();
          console.log('Usuários de login carregados do backend:', users);
          displayLoginAlunosTable(users);
      } catch (error) {
          console.error('Erro ao buscar usuários de login do backend:', error);
          const tbody = document.querySelector('#table_login_alunos tbody');
          if (tbody) {
              tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: red;">Erro ao carregar dados de login.</td></tr>`;
          }
      }
  }

  function displayLoginAlunosTable(users) {
      const tbody = document.querySelector('#table_login_alunos tbody');
      if (!tbody) {
          console.warn('Elemento tbody da tabela de login_alunos não encontrado.');
          return;
      }
      tbody.innerHTML = '';
      if (users.length === 0) {
          tbody.innerHTML = `<tr><td colspan="5" style="text-align: center;">Nenhum usuário de login encontrado.</td></tr>`;
          return;
      }

      users.forEach(user => {
          const lastLogin = user.last_login ? new Date(user.last_login).toLocaleString('pt-BR') : '';
          const row = document.createElement('tr');
          row.innerHTML = `
              <td>${user.username || ''}</td>
              <td>${user.full_name || ''}</td>
              <td>${lastLogin}</td>
              <td>${user.total_logins !== null ? user.total_logins : ''}</td>
              <td>${user.online_status || ''}</td>
          `;
          tbody.appendChild(row);
      });
  }

  // --- Chamada inicial para carregar os alunos (info_alunos) se estiver na página database.html ---
  if (window.location.pathname.endsWith('database.html')) {
      fetchAlunosFromBackend();
  }

  // --- LÓGICA PARA ADICIONAR ALUNO ---
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
      document.getElementById('addAlunoForm').reset();
  }

  const addAlunoForm = document.getElementById('addAlunoForm');
  if (addAlunoForm) {
      addAlunoForm.addEventListener('submit', async function(event) { // MODIFICAÇÃO: Adicionado 'async'
          event.preventDefault();

          const formData = new FormData(addAlunoForm);
          const alunoData = {};
          for (let [key, value] of formData.entries()) {
              alunoData[key] = value;
          }
          console.log('Dados do novo aluno a serem enviados:', alunoData);
          await sendAlunoToBackend(alunoData); // MODIFICAÇÃO: Adicionado 'await'
      });
  }

  async function sendAlunoToBackend(alunoData) { // MODIFICAÇÃO: Adicionado 'async'
      try {
          const response = await fetch('http://127.0.0.1:5000/alunos/add', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify(alunoData),
          });
          const data = await response.json();
          console.log('Resposta do backend:', data);
          if (data.success) {
              alert('Aluno adicionado com sucesso!');
              closeAddAlunoModal();
              fetchAlunosFromBackend(); // Recarrega a tabela
          } else {
              alert('Erro ao adicionar aluno: ' + (data.message || 'Erro desconhecido.'));
          }
      } catch (error) {
          console.error('Erro de rede ou servidor ao enviar aluno:', error);
          alert('Erro de conexão ou servidor ao tentar adicionar aluno. Verifique o console.');
      }
  }


  // --- LÓGICA PARA DELETAR ALUNO ---
  window.deleteAluno = async function(alunoId) { // MODIFICAÇÃO: Adicionado 'async'
      if (confirm(`Tem certeza que deseja excluir o aluno com ID ${alunoId}?`)) {
          try {
              const response = await fetch(`http://127.0.0.1:5000/alunos/delete/${alunoId}`, {
                  method: 'DELETE',
              });
              const data = await response.json();
              console.log('Resposta do backend (delete):', data);
              if (data.success) {
                  alert('Aluno excluído com sucesso!');
                  fetchAlunosFromBackend(); // Recarrega a tabela
              } else {
                  alert('Erro ao excluir aluno: ' + (data.message || 'Erro desconhecido.'));
              }
          } catch (error) {
              console.error('Erro de rede ou servidor ao excluir aluno:', error);
              alert('Erro de conexão ou servidor ao tentar excluir aluno.');
          }
      }
  };


  // --- LÓGICA PARA EDITAR ALUNO ---
  window.editAluno = async function(alunoId) { // MODIFICAÇÃO: Adicionado 'async'
      try {
          const response = await fetch(`http://127.0.0.1:5000/alunos/${alunoId}`);
          if (!response.ok) {
              throw new Error(`Erro HTTP! Status: ${response.status}`);
          }
          const aluno = await response.json();
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
      } catch (error) {
          console.error('Erro ao buscar dados do aluno para edição:', error);
          alert('Erro ao carregar dados do aluno para edição.');
      }
  };

  window.closeEditAlunoModal = function() {
      document.getElementById('editAlunoModal').classList.add('hidden');
      document.getElementById('editAlunoForm').reset();
  };

  const editAlunoForm = document.getElementById('editAlunoForm');
  if (editAlunoForm) {
      editAlunoForm.addEventListener('submit', async function(event) { // MODIFICAÇÃO: Adicionado 'async'
          event.preventDefault();

          const formData = new FormData(editAlunoForm);
          const alunoData = {};
          for (let [key, value] of formData.entries()) {
              if (key === 'data_nascimento' && value) {
                  alunoData[key] = value;
              } else {
                  alunoData[key] = value;
              }
          }

          const alunoId = alunoData.id;
          delete alunoData.id;

          console.log('Dados do aluno a serem atualizados:', alunoData, 'ID:', alunoId);
          await sendEditedAlunoToBackend(alunoId, alunoData); // MODIFICAÇÃO: Adicionado 'await'
      });
  }

  async function sendEditedAlunoToBackend(alunoId, alunoData) { // MODIFICAÇÃO: Adicionado 'async'
      try {
          const response = await fetch(`http://127.0.0.1:5000/alunos/edit/${alunoId}`, {
              method: 'PUT',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify(alunoData),
          });
          const data = await response.json();
          console.log('Resposta do backend (edição):', data);
          if (data.success) {
              alert('Aluno atualizado com sucesso!');
              closeEditAlunoModal();
              fetchAlunosFromBackend(); // Recarrega a tabela
          } else {
              alert('Erro ao atualizar aluno: ' + (data.message || 'Erro desconhecido.'));
          }
      } catch (error) {
          console.error('Erro de rede ou servidor ao atualizar aluno:', error);
          alert('Erro de conexão ou servidor ao tentar atualizar aluno. Verifique o console.');
      }
  }


  // --- Outras Funções ---
  function goBack() {
      window.history.back();
  }

  async function logout() { // MODIFICAÇÃO: Adicionado 'async'
    const userId = localStorage.getItem("userId"); // ADIÇÃO: Pega o ID do usuário logado
    if (userId) {
      try {
        await fetch(`http://127.0.0.1:5000/logout/${userId}`, { // ADIÇÃO: Chama o endpoint de logout
          method: 'POST',
        });
        console.log('Status online atualizado para offline.');
      } catch (error) {
        console.error('Erro ao atualizar status de logout:', error);
      }
    }
    localStorage.removeItem("isLoggedIn");
    localStorage.removeItem("userId"); // ADIÇÃO
    localStorage.removeItem("username");
    localStorage.removeItem("userRole");
    localStorage.removeItem("userName");
    localStorage.removeItem("userStudentId"); // ADIÇÃO
    window.location.href = "index.html";
  }

  const userAvatar = document.querySelector(".user-avatar");
  if (userAvatar) {
    userAvatar.addEventListener("click", () => {
      if (confirm("Deseja fazer logout?")) {
        logout();
      }
    });
    userAvatar.style.cursor = "pointer";
    userAvatar.title = "Clique para fazer logout";
  }

  function abrirWhatsApp() {
      const whatsappLink = "https://chat.whatsapp.com/GHZuEpQhb5uGFROPWioy9o?mode=ac_c";
      window.open(whatsappLink, '_blank');
  }

  // Fechar modals ao clicar fora ou pressionar ESC
  document.addEventListener('DOMContentLoaded', () => {
      const addAlunoModal = document.getElementById('addAlunoModal');
      if (addAlunoModal) { // ADIÇÃO: Verifica se o modal existe antes de adicionar listener
          addAlunoModal.addEventListener('click', (e) => {
              if (e.target === addAlunoModal) {
                  closeAddAlunoModal();
              }
          });
      }

      const editAlunoModal = document.getElementById('editAlunoModal');
      if (editAlunoModal) { // ADIÇÃO: Verifica se o modal existe antes de adicionar listener
          editAlunoModal.addEventListener('click', (e) => {
              if (e.target === editAlunoModal) {
                  closeEditAlunoModal();
              }
          });
      }

      document.addEventListener('keydown', (e) => {
          if (e.key === 'Escape') {
              if (addAlunoModal && !addAlunoModal.classList.contains('hidden')) {
                  closeAddAlunoModal();
              }
              if (editAlunoModal && !editAlunoModal.classList.contains('hidden')) {
                  closeEditAlunoModal();
              }
          }
      });
  });
}); // Fim do DOMContentLoaded

// Funções globais para serem acessíveis diretamente do HTML (onclick)
window.changeTable = function() {
    const selectedTable = document.getElementById('tableSelect').value;
    document.querySelectorAll('.database-table-container').forEach(table => {
        table.classList.add('hidden');
    });
    document.getElementById(`table_${selectedTable}`).classList.remove('hidden');

    // ADIÇÃO: Chamadas de fetch para as novas tabelas
    if (selectedTable === 'info_alunos') {
        window.fetchAlunosFromBackend();
    } else if (selectedTable === 'status_alunos') {
        window.fetchStudentOverallStatusFromBackend();
    } else if (selectedTable === 'login_alunos') {
        window.fetchLoginAlunosFromBackend();
    }
    // 'atividades_alunos' continuará estática por enquanto, se não for adicionada lógica de backend para ela.
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