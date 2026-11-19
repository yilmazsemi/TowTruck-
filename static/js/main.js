// Tow Truck JavaScript Etkileşimleri

document.addEventListener('DOMContentLoaded', function () {
    // Mobil Menü Toggle
    const mobileBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');

    if (mobileBtn && mobileMenu) {
        mobileBtn.addEventListener('click', function () {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // Dosya Yükleme Önizlemesi (Resim seçildiğinde göster)
    const fileInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function (e) {
            const previewContainer = document.getElementById(this.dataset.previewTarget || 'image-preview');
            if (!previewContainer) return;

            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (event) {
                    previewContainer.innerHTML = `
                        <div class="relative inline-block mt-3 rounded-lg overflow-hidden border border-amber-500/50 shadow-md">
                            <img src="${event.target.result}" class="w-32 h-24 object-cover" alt="Önizleme">
                            <span class="absolute top-1 right-1 bg-black/70 text-white text-[10px] px-1.5 py-0.5 rounded">Seçildi</span>
                        </div>
                    `;
                    previewContainer.classList.remove('hidden');
                };
                reader.readAsDataURL(file);
            }
        });
    });

    // Otomatik telefon formatlama yardımı (isteğe bağlı)
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('focus', function () {
            if (!this.value) {
                this.placeholder = '05XX XXX XX XX';
            }
        });
    });
});

// Resim Büyütme (Lightbox Modal) Fonksiyonu
function openImageModal(imgSrc, title, desc) {
    let modal = document.getElementById('image-lightbox-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'image-lightbox-modal';
        modal.className = 'fixed inset-0 z-50 bg-black/90 backdrop-blur-sm flex items-center justify-center p-4 transition-opacity';
        modal.innerHTML = `
            <div class="relative max-w-4xl w-full bg-gray-900 border border-gray-700 rounded-2xl overflow-hidden shadow-2xl">
                <button onclick="closeImageModal()" class="absolute top-3 right-3 z-10 w-10 h-10 rounded-full bg-black/70 hover:bg-red-600 text-white flex items-center justify-center transition-colors">
                    <i class="fa-solid fa-xmark text-lg"></i>
                </button>
                <div class="max-h-[75vh] bg-black flex items-center justify-center overflow-hidden">
                    <img id="lightbox-img" src="" alt="Büyütülmüş Fotoğraf" class="max-h-[75vh] w-auto object-contain">
                </div>
                <div class="p-5 bg-gray-900 border-t border-gray-800">
                    <h3 id="lightbox-title" class="text-lg font-bold text-white mb-1"></h3>
                    <p id="lightbox-desc" class="text-sm text-gray-400"></p>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        modal.addEventListener('click', function(e) {
            if (e.target === modal) closeImageModal();
        });
    }

    document.getElementById('lightbox-img').src = imgSrc;
    document.getElementById('lightbox-title').innerText = title || 'Kurtarma Fotoğrafı';
    document.getElementById('lightbox-desc').innerText = desc || '';
    modal.classList.remove('hidden');
}

function closeImageModal() {
    const modal = document.getElementById('image-lightbox-modal');
    if (modal) modal.classList.add('hidden');
}
