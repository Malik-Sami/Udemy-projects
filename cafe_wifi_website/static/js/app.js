/**
 * LaptopFriendly London - Interactive Client-Side Engine
 * Handles real-time filtering, live preview, modals, and Day 66 REST API testing.
 */

document.addEventListener('DOMContentLoaded', () => {
    // State
    const state = {
        cafes: window.INITIAL_CAFES || [],
        searchQuery: '',
        selectedLocation: '',
        sortBy: 'score',
        filters: {
            sockets: false,
            wifi: false,
            calls: false,
            toilet: false,
            spacious: false
        },
        viewMode: 'grid',
        theme: localStorage.getItem('lf_theme') || 'dark',
        deleteTargetId: null
    };

    // Elements
    const searchInput = document.getElementById('search-input');
    const clearSearchBtn = document.getElementById('clear-search-btn');
    const locationSelect = document.getElementById('location-select');
    const sortSelect = document.getElementById('sort-select');
    const viewGridBtn = document.getElementById('view-grid-btn');
    const viewListBtn = document.getElementById('view-list-btn');
    const filterClearAllBtn = document.getElementById('filter-clear-all');
    const cafesGrid = document.getElementById('cafes-grid');
    const resultsCount = document.getElementById('results-count');
    const emptyState = document.getElementById('empty-state');
    const themeToggleBtn = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');

    // Modals
    const modalAdd = document.getElementById('modal-add-cafe');
    const modalDetails = document.getElementById('modal-details-cafe');
    const modalDelete = document.getElementById('modal-delete-confirm');
    const modalApi = document.getElementById('modal-api-docs');

    // Initialize Theme
    applyTheme(state.theme);

    // Setup Event Listeners
    setupSearchAndFilters();
    setupLivePreview();
    setupThemeToggle();
    setupLuckyPick();
    setupApiTester();

    // -------------------------------------------------------------
    // Filter & Search Engine
    // -------------------------------------------------------------
    function setupSearchAndFilters() {
        // Search Input
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                state.searchQuery = e.target.value.toLowerCase().trim();
                clearSearchBtn.style.display = state.searchQuery ? 'block' : 'none';
                renderCafes();
            });
        }

        if (clearSearchBtn) {
            clearSearchBtn.addEventListener('click', () => {
                searchInput.value = '';
                state.searchQuery = '';
                clearSearchBtn.style.display = 'none';
                searchInput.focus();
                renderCafes();
            });
        }

        // Location Select
        if (locationSelect) {
            locationSelect.addEventListener('change', (e) => {
                state.selectedLocation = e.target.value;
                renderCafes();
            });
        }

        // Sort Select
        if (sortSelect) {
            sortSelect.addEventListener('change', (e) => {
                state.sortBy = e.target.value;
                renderCafes();
            });
        }

        // Amenity Chips
        const filterChips = document.querySelectorAll('.filter-chip[data-filter]');
        filterChips.forEach(chip => {
            chip.addEventListener('click', () => {
                const filterKey = chip.getAttribute('data-filter');
                state.filters[filterKey] = !state.filters[filterKey];
                chip.classList.toggle('active', state.filters[filterKey]);
                updateResetButtonVisibility();
                renderCafes();
            });
        });

        if (filterClearAllBtn) {
            filterClearAllBtn.addEventListener('click', resetAllFilters);
        }

        // Layout Switches
        if (viewGridBtn && viewListBtn) {
            viewGridBtn.addEventListener('click', () => {
                state.viewMode = 'grid';
                viewGridBtn.classList.add('active');
                viewListBtn.classList.remove('active');
                cafesGrid.classList.remove('list-view');
            });

            viewListBtn.addEventListener('click', () => {
                state.viewMode = 'list';
                viewListBtn.classList.add('active');
                viewGridBtn.classList.remove('active');
                cafesGrid.classList.add('list-view');
            });
        }
    }

    function updateResetButtonVisibility() {
        const hasActiveFilter = Object.values(state.filters).some(Boolean) || state.selectedLocation || state.searchQuery;
        if (filterClearAllBtn) {
            filterClearAllBtn.style.display = hasActiveFilter ? 'inline-flex' : 'none';
        }
    }

    window.resetAllFilters = function() {
        state.searchQuery = '';
        state.selectedLocation = '';
        state.sortBy = 'score';
        Object.keys(state.filters).forEach(k => state.filters[k] = false);

        if (searchInput) searchInput.value = '';
        if (clearSearchBtn) clearSearchBtn.style.display = 'none';
        if (locationSelect) locationSelect.value = '';
        if (sortSelect) sortSelect.value = 'score';

        document.querySelectorAll('.filter-chip[data-filter]').forEach(chip => chip.classList.remove('active'));
        if (filterClearAllBtn) filterClearAllBtn.style.display = 'none';

        renderCafes();
        showToast('Filters reset to default view.');
    };

    function parsePrice(priceStr) {
        if (!priceStr) return 0;
        const num = parseFloat(priceStr.replace(/[^0-9.]/g, ''));
        return isNaN(num) ? 0 : num;
    }

    function parseSeats(seatsStr) {
        if (!seatsStr) return 0;
        if (seatsStr.includes('50+')) return 55;
        const parts = seatsStr.split('-');
        if (parts.length > 1) {
            return parseInt(parts[1].trim(), 10) || 0;
        }
        return parseInt(seatsStr, 10) || 0;
    }

    function renderCafes() {
        // Filter elements
        const cards = Array.from(document.querySelectorAll('.cafe-card:not(.preview-card)'));
        let visibleCount = 0;

        // Collect matching items
        const matchingCards = [];

        cards.forEach(card => {
            const name = (card.getAttribute('data-name') || '').toLowerCase();
            const location = (card.getAttribute('data-location') || '').toLowerCase();
            const seats = card.getAttribute('data-seats') || '';
            const sockets = card.getAttribute('data-sockets') === 'true';
            const wifi = card.getAttribute('data-wifi') === 'true';
            const calls = card.getAttribute('data-calls') === 'true';
            const toilet = card.getAttribute('data-toilet') === 'true';

            // Query check
            const matchesQuery = !state.searchQuery || name.includes(state.searchQuery) || location.includes(state.searchQuery);

            // Location check
            const matchesLocation = !state.selectedLocation || location.includes(state.selectedLocation.toLowerCase());

            // Amenities check
            const matchesSockets = !state.filters.sockets || sockets;
            const matchesWifi = !state.filters.wifi || wifi;
            const matchesCalls = !state.filters.calls || calls;
            const matchesToilet = !state.filters.toilet || toilet;
            const matchesSpacious = !state.filters.spacious || (seats.includes('30') || seats.includes('40') || seats.includes('50+'));

            const isMatch = matchesQuery && matchesLocation && matchesSockets && matchesWifi && matchesCalls && matchesToilet && matchesSpacious;

            if (isMatch) {
                card.style.display = 'flex';
                matchingCards.push(card);
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });

        // Sorting matching cards
        matchingCards.sort((a, b) => {
            if (state.sortBy === 'name-asc') {
                return (a.getAttribute('data-name') || '').localeCompare(b.getAttribute('data-name') || '');
            } else if (state.sortBy === 'price-asc') {
                return parsePrice(a.getAttribute('data-price')) - parsePrice(b.getAttribute('data-price'));
            } else if (state.sortBy === 'price-desc') {
                return parsePrice(b.getAttribute('data-price')) - parsePrice(a.getAttribute('data-price'));
            } else if (state.sortBy === 'seats-desc') {
                return parseSeats(b.getAttribute('data-seats')) - parseSeats(a.getAttribute('data-seats'));
            } else {
                // Top work score
                return parseInt(b.getAttribute('data-score') || '0', 10) - parseInt(a.getAttribute('data-score') || '0', 10);
            }
        });

        // Re-append in sorted order
        matchingCards.forEach(card => cafesGrid.appendChild(card));

        // Update UI counters
        if (resultsCount) {
            resultsCount.textContent = `Showing ${visibleCount} cafe${visibleCount === 1 ? '' : 's'}`;
        }

        if (emptyState) {
            emptyState.style.display = visibleCount === 0 ? 'block' : 'none';
        }

        updateResetButtonVisibility();
    }

    // -------------------------------------------------------------
    // Live Preview for "Add Cafe" Modal
    // -------------------------------------------------------------
    function setupLivePreview() {
        const formName = document.getElementById('form-name');
        const formLocation = document.getElementById('form-location');
        const formPrice = document.getElementById('form-price');
        const formSeats = document.getElementById('form-seats');
        const formImg = document.getElementById('form-img');

        const formWifi = document.getElementById('form-has-wifi');
        const formSockets = document.getElementById('form-has-sockets');
        const formCalls = document.getElementById('form-can-calls');
        const formToilet = document.getElementById('form-has-toilet');

        const prevName = document.getElementById('prev-name');
        const prevLocation = document.getElementById('prev-location');
        const prevPrice = document.getElementById('prev-price');
        const prevSeats = document.getElementById('prev-seats');
        const prevImg = document.getElementById('prev-img');
        const prevScore = document.getElementById('prev-score');

        const prevWifi = document.getElementById('prev-amenity-wifi');
        const prevSockets = document.getElementById('prev-amenity-sockets');
        const prevCalls = document.getElementById('prev-amenity-calls');
        const prevToilet = document.getElementById('prev-amenity-toilet');

        function updatePreview() {
            if (prevName && formName) prevName.textContent = formName.value.trim() || 'Your Cafe Name';
            if (prevLocation && formLocation) {
                prevLocation.innerHTML = `<i class="fa-solid fa-location-dot"></i> ${formLocation.value.trim() || 'Neighborhood'}`;
            }
            if (prevPrice && formPrice) prevPrice.textContent = formPrice.value.trim() || '£2.80';
            if (prevSeats && formSeats) prevSeats.textContent = `${formSeats.value} seats`;
            if (prevImg && formImg && formImg.value.trim()) {
                prevImg.src = formImg.value.trim();
            }

            // Amenities
            const hasWifi = formWifi ? formWifi.checked : true;
            const hasSockets = formSockets ? formSockets.checked : true;
            const canCalls = formCalls ? formCalls.checked : false;
            const hasToilet = formToilet ? formToilet.checked : true;

            if (prevWifi) {
                prevWifi.className = `amenity-item ${hasWifi ? 'active' : 'inactive'}`;
                prevWifi.innerHTML = `<i class="fa-solid fa-wifi"></i> <span>${hasWifi ? 'Wi-Fi' : 'No Wi-Fi'}</span>`;
            }
            if (prevSockets) {
                prevSockets.className = `amenity-item ${hasSockets ? 'active' : 'inactive'}`;
                prevSockets.innerHTML = `<i class="fa-solid fa-plug"></i> <span>${hasSockets ? 'Sockets' : 'No Sockets'}</span>`;
            }
            if (prevCalls) {
                prevCalls.className = `amenity-item ${canCalls ? 'active' : 'inactive'}`;
                prevCalls.innerHTML = `<i class="fa-solid fa-phone"></i> <span>${canCalls ? 'Calls OK' : 'Quiet'}</span>`;
            }
            if (prevToilet) {
                prevToilet.className = `amenity-item ${hasToilet ? 'active' : 'inactive'}`;
                prevToilet.innerHTML = `<i class="fa-solid fa-restroom"></i> <span>${hasToilet ? 'Restroom' : 'No WC'}</span>`;
            }

            // Score calculation
            let score = 0;
            if (hasWifi) score += 3;
            if (hasSockets) score += 3;
            if (canCalls) score += 2;
            if (hasToilet) score += 1;
            if (formSeats && (formSeats.value.includes('30') || formSeats.value.includes('40') || formSeats.value.includes('50+'))) score += 1;

            if (prevScore) {
                prevScore.innerHTML = `<i class="fa-solid fa-bolt"></i> ${Math.min(score, 10)}/10`;
            }
        }

        [formName, formLocation, formPrice, formSeats, formImg].forEach(el => {
            if (el) el.addEventListener('input', updatePreview);
        });

        [formWifi, formSockets, formCalls, formToilet].forEach(el => {
            if (el) el.addEventListener('change', updatePreview);
        });

        window.applyImagePreset = function(url) {
            if (formImg) {
                formImg.value = url;
                updatePreview();
            }
        };
    }

    // -------------------------------------------------------------
    // Modal Helpers
    // -------------------------------------------------------------
    const btnOpenAddModal = document.getElementById('btn-open-add-modal');
    if (btnOpenAddModal) {
        btnOpenAddModal.addEventListener('click', () => {
            if (modalAdd) modalAdd.classList.add('open');
        });
    }

    window.closeAddModal = function() {
        if (modalAdd) modalAdd.classList.remove('open');
    };

    window.closeDetailsModal = function() {
        if (modalDetails) modalDetails.classList.remove('open');
    };

    window.closeDeleteModal = function() {
        if (modalDelete) modalDelete.classList.remove('open');
        state.deleteTargetId = null;
    };

    window.openApiModal = function() {
        if (modalApi) modalApi.classList.add('open');
    };

    window.closeApiModal = function() {
        if (modalApi) modalApi.classList.remove('open');
    };

    const btnApiModal = document.getElementById('btn-api-modal');
    if (btnApiModal) {
        btnApiModal.addEventListener('click', window.openApiModal);
    }

    // Close on backdrop click or ESC
    document.querySelectorAll('.modal-backdrop').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('open');
            }
        });
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal-backdrop.open').forEach(modal => {
                modal.classList.remove('open');
            });
        }
    });

    // -------------------------------------------------------------
    // Cafe Details Modal
    // -------------------------------------------------------------
    window.openCafeDetails = function(cafeId) {
        const cafe = state.cafes.find(c => c.id === cafeId);
        if (!cafe) return;

        const titleEl = document.getElementById('detail-modal-name');
        const locEl = document.getElementById('detail-modal-location');
        const contentEl = document.getElementById('detail-modal-content');

        if (titleEl) titleEl.textContent = cafe.name;
        if (locEl) locEl.textContent = `${cafe.location}, London`;

        if (contentEl) {
            contentEl.innerHTML = `
                <div style="margin-bottom: 1.5rem; border-radius: 12px; overflow: hidden; height: 240px; position: relative;">
                    <img src="${cafe.img_url}" alt="${cafe.name}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.onerror=null; this.src='/static/images/default_cafe.jpg';">
                    <span style="position: absolute; top: 1rem; right: 1rem; background: #f59e0b; color: #fff; font-weight: 800; padding: 0.35rem 0.85rem; border-radius: 9999px; box-shadow: 0 4px 12px rgba(245,158,11,0.5);">
                        <i class="fa-solid fa-bolt"></i> ${cafe.work_score}/10 Work Rating
                    </span>
                </div>

                <h3 style="font-family: var(--font-heading); margin-bottom: 0.75rem;">Amenities & Work Features</h3>
                <div class="amenities-grid" style="margin-bottom: 1.5rem;">
                    <div class="amenity-item ${cafe.has_wifi ? 'active' : 'inactive'}">
                        <i class="fa-solid fa-wifi"></i> <span>${cafe.has_wifi ? 'High-Speed Wi-Fi Verified' : 'No Wi-Fi Reported'}</span>
                    </div>
                    <div class="amenity-item ${cafe.has_sockets ? 'active' : 'inactive'}">
                        <i class="fa-solid fa-plug"></i> <span>${cafe.has_sockets ? 'Power Sockets Available' : 'Limited / No Sockets'}</span>
                    </div>
                    <div class="amenity-item ${cafe.can_take_calls ? 'active' : 'inactive'}">
                        <i class="fa-solid fa-phone"></i> <span>${cafe.can_take_calls ? 'Call Friendly Environment' : 'Quiet Zone (No Voice Calls)'}</span>
                    </div>
                    <div class="amenity-item ${cafe.has_toilet ? 'active' : 'inactive'}">
                        <i class="fa-solid fa-restroom"></i> <span>${cafe.has_toilet ? 'Customer Restroom Available' : 'No Dedicated WC'}</span>
                    </div>
                </div>

                <div style="background: var(--bg-surface-elevated); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.25rem; margin-bottom: 1.5rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.65rem;">
                        <span style="color: var(--text-secondary);"><i class="fa-solid fa-chair"></i> Seating Capacity:</span>
                        <strong style="color: var(--text-primary);">${cafe.seats} seats</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.65rem;">
                        <span style="color: var(--text-secondary);"><i class="fa-solid fa-mug-hot"></i> Coffee Price (Espresso/Flat White):</span>
                        <strong style="color: var(--accent-primary); font-size: 1.05rem;">${cafe.coffee_price}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-secondary);"><i class="fa-solid fa-location-dot"></i> Borough Area:</span>
                        <strong style="color: var(--text-primary);">${cafe.location}</strong>
                    </div>
                </div>

                <div style="display: flex; gap: 0.75rem;">
                    <a href="${cafe.map_url}" target="_blank" rel="noopener noreferrer" class="btn btn-primary" style="flex: 1;">
                        <i class="fa-solid fa-diamond-turn-right"></i> Open in Google Maps
                    </a>
                    <button type="button" class="btn btn-glass" onclick="copyMapLink('${cafe.map_url}', '${cafe.name}')">
                        <i class="fa-regular fa-copy"></i> Copy Link
                    </button>
                </div>
            `;
        }

        if (modalDetails) modalDetails.classList.add('open');
    };

    // -------------------------------------------------------------
    // Delete Cafe Confirmation & Action
    // -------------------------------------------------------------
    window.confirmDeleteCafe = function(cafeId, cafeName) {
        state.deleteTargetId = cafeId;
        const nameEl = document.getElementById('delete-cafe-name');
        if (nameEl) nameEl.textContent = `"${cafeName}"`;
        if (modalDelete) modalDelete.classList.add('open');
    };

    const btnConfirmDelete = document.getElementById('btn-confirm-delete-action');
    if (btnConfirmDelete) {
        btnConfirmDelete.addEventListener('click', async () => {
            if (!state.deleteTargetId) return;

            const apiKey = (document.getElementById('delete-api-key') || {}).value || 'TopSecretAPIKey';
            btnConfirmDelete.disabled = true;
            btnConfirmDelete.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Deleting...';

            try {
                const response = await fetch(`/api/delete/${state.deleteTargetId}?api-key=${encodeURIComponent(apiKey)}`, {
                    method: 'DELETE'
                });

                const data = await response.json();

                if (response.ok) {
                    const card = document.getElementById(`cafe-card-${state.deleteTargetId}`);
                    if (card) {
                        card.style.transition = 'all 0.4s ease';
                        card.style.opacity = '0';
                        card.style.transform = 'scale(0.85)';
                        setTimeout(() => {
                            card.remove();
                            // Update local state
                            state.cafes = state.cafes.filter(c => c.id !== state.deleteTargetId);
                            renderCafes();
                            // Update total stat
                            const statTotal = document.getElementById('stat-total');
                            if (statTotal) statTotal.textContent = state.cafes.length;
                        }, 400);
                    }

                    showToast(data.response ? data.response.success : 'Cafe removed successfully.');
                    closeDeleteModal();
                } else {
                    alert(data.error ? (data.error.Forbidden || JSON.stringify(data.error)) : 'Could not delete cafe.');
                }
            } catch (err) {
                console.error(err);
                alert('Network error while deleting cafe.');
            } finally {
                btnConfirmDelete.disabled = false;
                btnConfirmDelete.innerHTML = '<i class="fa-solid fa-trash"></i> Delete Cafe';
            }
        });
    }

    // -------------------------------------------------------------
    // Copy Map Link
    // -------------------------------------------------------------
    window.copyMapLink = function(url, name) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(url).then(() => {
                showToast(`📋 Copied Google Maps link for ${name}!`);
            }).catch(() => {
                promptCopyFallback(url);
            });
        } else {
            promptCopyFallback(url);
        }
    };

    function promptCopyFallback(text) {
        prompt('Copy this link:', text);
    }

    // -------------------------------------------------------------
    // Toast Notification System
    // -------------------------------------------------------------
    function showToast(message) {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.innerHTML = `<i class="fa-solid fa-circle-check"></i> <span>${message}</span>`;

        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3200);
    }

    // -------------------------------------------------------------
    // Lucky Pick (Random Cafe Selector)
    // -------------------------------------------------------------
    function setupLuckyPick() {
        const luckyBtn = document.getElementById('btn-lucky-pick');
        if (!luckyBtn) return;

        luckyBtn.addEventListener('click', async () => {
            luckyBtn.innerHTML = '<i class="fa-solid fa-dice fa-spin"></i> Rolling...';
            try {
                const response = await fetch('/api/random');
                const data = await response.json();
                if (data.cafe) {
                    showToast(`🎲 Lucky Spot Picked: ${data.cafe.name}!`);
                    // Open its details modal
                    openCafeDetails(data.cafe.id);

                    // Also highlight the card if visible
                    const card = document.getElementById(`cafe-card-${data.cafe.id}`);
                    if (card) {
                        card.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        card.style.outline = '3px solid #f59e0b';
                        card.style.boxShadow = '0 0 30px rgba(245, 158, 11, 0.6)';
                        setTimeout(() => {
                            card.style.outline = '';
                            card.style.boxShadow = '';
                        }, 2500);
                    }
                }
            } catch (err) {
                console.error(err);
            } finally {
                luckyBtn.innerHTML = '<i class="fa-solid fa-dice"></i> <span>Lucky Pick</span>';
            }
        });
    }

    // -------------------------------------------------------------
    // Theme Switcher (Dark / Light)
    // -------------------------------------------------------------
    function applyTheme(theme) {
        state.theme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('lf_theme', theme);

        if (themeIcon) {
            themeIcon.className = theme === 'dark' ? 'fa-solid fa-moon' : 'fa-solid fa-sun';
        }
    }

    function setupThemeToggle() {
        if (!themeToggleBtn) return;
        themeToggleBtn.addEventListener('click', () => {
            const newTheme = state.theme === 'dark' ? 'light' : 'dark';
            applyTheme(newTheme);
            showToast(`Switched to ${newTheme === 'dark' ? 'Espresso Dark' : 'Cream Light'} theme.`);
        });
    }

    // -------------------------------------------------------------
    // REST API Live Tester
    // -------------------------------------------------------------
    function setupApiTester() {
        window.testApiEndpoint = async function(endpoint) {
            const consoleWrap = document.getElementById('api-console-wrap');
            const testedUrl = document.getElementById('api-tested-url');
            const codeEl = document.getElementById('api-console-code');

            if (consoleWrap) consoleWrap.style.display = 'block';
            if (testedUrl) testedUrl.textContent = endpoint;
            if (codeEl) codeEl.textContent = 'Loading response...';

            try {
                const res = await fetch(endpoint);
                const data = await res.json();
                if (codeEl) {
                    codeEl.textContent = JSON.stringify(data, null, 2);
                }
            } catch (err) {
                if (codeEl) codeEl.textContent = `Error: ${err.message}`;
            }
        };

        window.copyConsoleOutput = function() {
            const codeEl = document.getElementById('api-console-code');
            if (codeEl && codeEl.textContent) {
                navigator.clipboard.writeText(codeEl.textContent).then(() => {
                    showToast('📋 API Response copied to clipboard!');
                });
            }
        };
    }
});
