/** @odoo-module **/
// =============================================================================
// website_360_viewer.js — Frontend 360° Panorama Viewer
// =============================================================================
// Uses Odoo 17 publicWidget to initialize Pannellum on the product page.
// Pannellum is loaded from static/lib/ as a plain global script.
// =============================================================================

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.Website360Viewer = publicWidget.Widget.extend({
    selector: ".o_360_viewer_wrapper",

    start: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            self.container = self.el.querySelector("#panorama_viewer");
            if (!self.container) {
                console.warn("[360 View] No #panorama_viewer found inside wrapper.");
                return;
            }

            // Read config from data attributes
            self.imageUrl = self.container.dataset.imageUrl || "";
            self.autoRotate = self.container.dataset.autoRotate === "true";
            self.defaultFov = parseInt(self.container.dataset.defaultFov) || 100;
            self.scenesJson = self.container.dataset.scenesJson || "";

            if (!self.imageUrl && !self.scenesJson) {
                console.warn("[360 View] No image URL or scenes JSON provided.");
                return;
            }

            console.log("[360 View] Config loaded. imageUrl:", self.imageUrl,
                        "autoRotate:", self.autoRotate, "scenesJson:", !!self.scenesJson);

            // Dynamically load pannellum then init
            self._loadPannellum(function () {
                self._initViewer();
                self._setupToggle();
                // After Pannellum creates its DOM, protect it from Odoo
                self._protectFromOdoo();
            });
        });
    },

    // -------------------------------------------------------------------------
    // Protect viewer from Odoo — stop events from bubbling UP past wrapper.
    // IMPORTANT: mousemove/mouseup must NOT be stopped here because Pannellum
    // registers document-level listeners for drag that need those events!
    // -------------------------------------------------------------------------
    _protectFromOdoo: function () {
        var wrapper = this.el;

        // Mark non-editable for website editor
        wrapper.setAttribute("contenteditable", "false");
        wrapper.classList.add("o_not_editable");

        // Only stop propagation for events Odoo might hijack at parent level.
        // DO NOT include mousemove/mouseup/pointermove/pointerup — Pannellum
        // needs these to bubble all the way to document for drag to work.
        var eventNames = [
            "click", "dblclick",
            "wheel", "contextmenu",
        ];

        eventNames.forEach(function (name) {
            wrapper.addEventListener(name, function (e) {
                e.stopPropagation();
            }, false);
        });

        console.log("[360 View] Protected wrapper from Odoo event bubbling.");
    },

    // -------------------------------------------------------------------------
    // Load Pannellum dynamically via fetch + inline script
    // -------------------------------------------------------------------------
    _loadPannellum: function (callback) {
        // Already loaded?
        if (window.pannellum) {
            console.log("[360 View] Pannellum already available.");
            callback();
            return;
        }

        var basePath = "/website_360_view/static/lib/pannellum/";
        var cacheBust = "?v=" + Date.now();

        // Inject CSS if not already present
        if (!document.querySelector('link[href*="pannellum.css"]')) {
            var link = document.createElement("link");
            link.rel = "stylesheet";
            link.href = basePath + "pannellum.css" + cacheBust;
            document.head.appendChild(link);
            console.log("[360 View] Injected pannellum.css");
        }

        // Fetch JS source and inject as inline script to guarantee
        // window.pannellum global is set (avoids Odoo intercepting <script src>)
        console.log("[360 View] Fetching pannellum.js via fetch()...");
        fetch(basePath + "pannellum.js" + cacheBust)
            .then(function (response) {
                if (!response.ok) {
                    throw new Error("HTTP " + response.status);
                }
                return response.text();
            })
            .then(function (code) {
                console.log("[360 View] Fetched pannellum.js (" + code.length + " chars). Executing...");
                // Execute as inline script in global scope
                var script = document.createElement("script");
                script.textContent = code;
                document.head.appendChild(script);

                console.log("[360 View] After inline exec: window.libpannellum =", !!window.libpannellum,
                            "window.pannellum =", !!window.pannellum);
                if (window.pannellum) {
                    callback();
                } else {
                    console.error("[360 View] pannellum.js executed but window.pannellum not defined.");
                }
            })
            .catch(function (err) {
                console.error("[360 View] Failed to fetch pannellum.js:", err);
            });
    },

    // -------------------------------------------------------------------------
    // Viewer initialization
    // -------------------------------------------------------------------------
    _initViewer: function () {
        if (!window.pannellum) {
            this._showError("Pannellum library not loaded.");
            return;
        }

        // Remove loading spinner
        var loading = this.container.querySelector(".o_360_loading");
        if (loading) loading.remove();

        try {
            if (this.scenesJson && this.scenesJson.trim().length > 2) {
                this._initMultiScene();
            } else {
                this._initSingleScene();
            }
            console.log("[360 View] Viewer initialized successfully.");
        } catch (e) {
            console.error("[360 View] Init failed:", e);
            this._showError("Failed to initialize 360° viewer.");
        }
    },

    _initSingleScene: function () {
        this.viewer = window.pannellum.viewer(this.container, {
            type: "equirectangular",
            panorama: this.imageUrl,
            autoLoad: true,
            autoRotate: this.autoRotate ? -2 : 0,
            hfov: this.defaultFov,
            compass: false,
            showZoomCtrl: true,
            showFullscreenCtrl: true,
            mouseZoom: true,
            draggable: true,
            friction: 0.15,
            yaw: 0,
            pitch: 0,
            minHfov: 30,
            maxHfov: 120,
        });
    },

    _initMultiScene: function () {
        var scenes = {};
        var firstSceneId = "";

        try {
            var arr = JSON.parse(this.scenesJson);
            if (!Array.isArray(arr) || arr.length === 0) {
                this._initSingleScene();
                return;
            }

            firstSceneId = arr[0].id || "scene0";

            arr.forEach(function (s, i) {
                var id = s.id || ("scene" + i);
                scenes[id] = {
                    title: s.title || ("Scene " + (i + 1)),
                    type: "equirectangular",
                    panorama: s.image || s.panorama || "",
                    hotSpots: (s.hotSpots || []).map(function (h) {
                        // Auto-detect type: scene transition or URL link or info
                        var type = h.type;
                        if (!type) {
                            if (h.sceneId) type = "scene";
                            else if (h.url) type = "url";
                            else type = "info";
                        }
                        return {
                            pitch: h.pitch || 0,
                            yaw: h.yaw || 0,
                            type: type,
                            text: h.text || "",
                            sceneId: h.sceneId || undefined,
                            URL: h.url || undefined,
                        };
                    }),
                };
            });
        } catch (e) {
            console.error("[360 View] Invalid scenes JSON:", e);
            this._initSingleScene();
            return;
        }

        this.viewer = window.pannellum.viewer(this.container, {
            default: {
                firstScene: firstSceneId,
                autoLoad: true,
                autoRotate: this.autoRotate ? -2 : 0,
                hfov: this.defaultFov,
                showZoomCtrl: true,
                showFullscreenCtrl: true,
                draggable: true,
            },
            scenes: scenes,
        });
    },

    // -------------------------------------------------------------------------
    // Toggle between 360 and normal images
    // -------------------------------------------------------------------------
    _setupToggle: function () {
        var self = this;
        var btn = this.el.querySelector(".o_360_toggle_btn");
        if (!btn) return;

        btn.addEventListener("click", function (e) {
            e.preventDefault();
            e.stopPropagation();
            var wrapper = self.el;
            var mode = btn.dataset.mode;

            if (mode === "360") {
                wrapper.querySelector("#panorama_viewer").style.display = "none";
                btn.dataset.mode = "normal";
                btn.innerHTML = '<i class="fa fa-globe me-1"></i>Switch to 360° view';
            } else {
                wrapper.querySelector("#panorama_viewer").style.display = "";
                btn.dataset.mode = "360";
                btn.innerHTML = '<i class="fa fa-image me-1"></i>Switch to normal images';
                if (self.viewer) self.viewer.resize();
            }
        });
    },

    _showError: function (msg) {
        this.container.innerHTML =
            '<div class="alert alert-warning text-center m-3">' +
            '<i class="fa fa-exclamation-triangle me-2"></i>' +
            (msg || "Unable to load 360° viewer.") +
            "</div>";
    },

    destroy: function () {
        if (this.viewer) {
            try { this.viewer.destroy(); } catch (e) { /* ok */ }
        }
        this._super.apply(this, arguments);
    },
});

export default publicWidget.registry.Website360Viewer;
