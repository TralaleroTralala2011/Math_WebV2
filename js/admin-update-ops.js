/* Admin-only update controls. All authorization and validation happen server-side. */
(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const apiBase = window.MATHWEB_API_URL || 'http://127.0.0.1:8000';
  const token = () => localStorage.getItem('mathweb_admin_token');
  const message = (id, value, isError = false) => {
    const el = $(id);
    if (!el) return;
    el.textContent = value;
    el.className = 'notice ' + (isError ? 'error' : 'ok');
    el.classList.remove('hidden');
  };
  const readError = async (res) => {
    let reason = 'HTTP ' + res.status;
    try { const data = await res.json(); reason = data.detail || data.message || reason; } catch (_) {}
    throw new Error(typeof reason === 'string' ? reason : JSON.stringify(reason));
  };
  async function request(path, body, expectBlob = false) {
    const auth = token();
    if (!auth) throw new Error('Cần đăng nhập bằng tài khoản Admin.');
    const response = await fetch(apiBase + '/api/admin/update/' + path, {
      method: 'POST',
      headers: { Authorization: 'Bearer ' + auth },
      body,
      cache: 'no-store'
    });
    if (!response.ok) await readError(response);
    return expectBlob ? response.blob() : response.json();
  }
  const backupButton = $('mwUpdateBackupBtn');
  const restoreButton = $('mwUpdateRestoreBtn');
  if (!backupButton || !restoreButton) return;
  backupButton.addEventListener('click', async () => {
    const password = $('mwUpdateBackupPass').value;
    if (password.length < 12) return message('mwUpdateBackupStatus', 'Mật khẩu sao lưu cần ít nhất 12 ký tự.', true);
    backupButton.disabled = true;
    message('mwUpdateBackupStatus', 'Đang tạo bản sao lưu được mã hóa…');
    try {
      const form = new FormData(); form.append('passphrase', password);
      const blob = await request('backup', form, true);
      if (!blob.size) throw new Error('Tệp sao lưu trống, chưa thể gửi thông báo.');
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'MATH_WEB_FULL_BACKUP_' + new Date().toISOString().replace(/[:.]/g, '-') + '.mwbackup';
      document.body.appendChild(link);
      link.click(); link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000 * 60);
      // The browser can initiate a download, but cannot guarantee a user saved it.
      const announce = await request('announce', new FormData());
      message('mwUpdateBackupStatus', 'Đã khởi tạo tải bản sao lưu. ' + (announce.message || '') + ' Hãy kiểm tra thư mục Tải xuống trước khi cập nhật.');
    } catch (error) {
      message('mwUpdateBackupStatus', error.message, true);
    } finally {
      $('mwUpdateBackupPass').value = '';
      backupButton.disabled = false;
    }
  });
  restoreButton.addEventListener('click', async () => {
    const file = $('mwUpdateFile').files[0], passphrase = $('mwUpdateRestorePass').value;
    if (!file || !passphrase) return message('mwUpdateRestoreStatus', 'Cần chọn bản sao lưu và nhập mật khẩu tệp.', true);
    if (!file.name.toLowerCase().endsWith('.mwbackup')) return message('mwUpdateRestoreStatus', 'Chỉ chấp nhận tệp .mwbackup.', true);
    if (!confirm('Khôi phục sẽ ghi đè dữ liệu server đang có. Bạn đã sao lưu dữ liệu mới nhất chưa?')) return;
    if (prompt('Để khôi phục, gõ KHOI PHUC DU LIEU') !== 'KHOI PHUC DU LIEU') return;
    restoreButton.disabled = true;
    message('mwUpdateRestoreStatus', 'Đang kiểm tra và khôi phục cơ sở dữ liệu…');
    try {
      const form = new FormData();
      form.append('file', file); form.append('passphrase', passphrase); form.append('confirmation', 'KHOI PHUC DU LIEU');
      const result = await request('restore', form);
      message('mwUpdateRestoreStatus', (result.message || 'Khôi phục thành công.') + ' Các kho: ' + (result.restored || []).join(', '));
    } catch (error) {
      message('mwUpdateRestoreStatus', error.message, true);
    } finally {
      $('mwUpdateRestorePass').value = '';
      restoreButton.disabled = false;
    }
  });
})();
