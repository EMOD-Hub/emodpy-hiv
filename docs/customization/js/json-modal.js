(function () {
    function showModal(content) {
        var overlay = document.createElement('div');
        overlay.className = 'json-modal-overlay';

        var modal = document.createElement('div');
        modal.className = 'json-modal';

        var closeBtn = document.createElement('button');
        closeBtn.className = 'json-modal-close';
        closeBtn.setAttribute('aria-label', 'Close');
        closeBtn.textContent = '×';

        var pre = document.createElement('pre');
        var code = document.createElement('code');
        code.textContent = content;
        pre.appendChild(code);

        modal.appendChild(closeBtn);
        modal.appendChild(pre);
        overlay.appendChild(modal);
        document.body.appendChild(overlay);

        function close() { overlay.remove(); }

        closeBtn.addEventListener('click', close);
        overlay.addEventListener('click', function (e) {
            if (e.target === overlay) close();
        });
        document.addEventListener('keydown', function handler(e) {
            if (e.key === 'Escape') {
                close();
                document.removeEventListener('keydown', handler);
            }
        });
    }

    document.addEventListener('click', function (e) {
        var link = e.target.closest('a');
        if (!link) return;
        var href = link.getAttribute('href');
        if (!href || !href.match(/\.json(\?.*)?$/)) return;

        e.preventDefault();

        var url = new URL(href, window.location.href);
        fetch(url)
            .then(function (r) { return r.text(); })
            .then(function (text) {
                try {
                    text = JSON.stringify(JSON.parse(text), null, 4);
                } catch (_) {}
                showModal(text);
            })
            .catch(function () {
                showModal('Could not load ' + url.pathname);
            });
    });
})();
