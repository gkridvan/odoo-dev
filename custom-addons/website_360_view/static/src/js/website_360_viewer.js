/** @odoo-module **/
// =============================================================================
// website_360_viewer.js — Frontend 360° Panorama Viewer
// =============================================================================
// This script initializes the Pannellum viewer on the product page.
//
// HOW ODOO 17 FRONTEND JS WORKS:
//   Odoo 17 uses ES modules (OWL framework). For website frontend code,
//   we use publicWidget which is the standard way to attach JS behavior
//   to website DOM elements.
//
// PANNELLUM (https://pannellum.org/):
//   Lightweight, open-source, MIT-licensed panorama viewer.
//   Supports equirectangular images, hotspots, multi-scene, tours.
//   We load it as a static lib in our module (no external CDN dependency).
//
// DATA FLOW:
//   1. QWeb template renders data-* attributes on #panorama_viewer
//   2. This JS reads those attributes
//   3. Pannellum is initialized with the configuration
//   4. Toggle button lets users switch between 360° and normal images
// =============================================================================

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.Website360Viewer = publicWidget.Widget.extend({
    // Attach this widget to our panorama container
    selector: "#panorama_viewer",

    /**
     * Called when the DOM element is ready.
     * We read configuration from data attributes and initialize Pannellum.
     */
    start: function () {
        var self = this;
        this._super.apply(this, arguments);

        // Read configuration from data-* attributes set by QWeb template
        this.imageUrl = this.el.dataset.imageUrl || "";
        this.autoRotate = this.el.dataset.autoRotate === "true";
        this.defaultFov = parseInt(this.el.dataset.defaultFov) || 100;
        this.scenesJson = this.el.dataset.scenesJson || "";

        if (!this.imageUrl && !this.scenesJson) {
            console.warn("[360 View] No image URL or scenes JSON provided.");
            return;
        }

        // Wait for Pannellum to be available (it loads asynchronously)
        this._waitForPannellum().then(function () {
            self._initViewer();
            self._bindToggleButton();
        });
    },

    // -------------------------------------------------------------------------
    // Private Methods
    // -------------------------------------------------------------------------

    /**
     * Wait for the Pannellum global to be available.
     * Since assets load in parallel, Pannellum might not be ready yet.
     */
    _waitForPannellum: function () {
        return new Promise(function (resolve) {
            var attempts = 0;
            var check = setInterval(function () {
                if (window.pannellum || attempts > 50) {
                    clearInterval(check);
                    resolve();
                }
                attempts++;
            }, 100);
        });
    },

    /**
     * Initialize the Pannellum viewer with the product's configuration.
     */
    _initViewer: function () {
        if (!window.pannellum) {
            console.error("[360 View] Pannellum library not loaded!");
            this._showError();
            return;
        }

        // Remove the loading spinner
        var loading = this.el.querySelector(".o_360_loading");
        if (loading) loading.remove();

        try {
            // Check if multi-scene mode
            if (this.scenesJson) {
                this._initMultiScene();
            } else {
                this._initSingleScene();
            }
        } catch (e) {
            console.error("[360 View] Failed to initialize viewer:", e);
            this._showError();
        }
    },

    /**
     * Single panorama image mode (most common use case).
     */
    _initSingleScene: function () {
        this.viewer = window.pannellum.viewer(this.el, {
            type: "equirectangular",
            panorama: this.imageUrl,
            autoLoad: true,
            autoRotate: this.autoRotate ? -2 : 0,  // -2 = slow counter-clockwise
            hfov: this.defaultFov,
            compass: false,
            showZoomCtrl: true,
            showFullscreenCtrl: true,
            mouseZoom: true,
            // Responsive: fill the container
            friction: 0.15,
            yaw: 0,
            pitch: 0,
            minHfov: 30,
            maxHfov: 120,
        });
    },

    /**
     * Multi-scene mode with hotspots (advanced).
     * 
     * Expected JSON format:
     * [
     *   {
     *     "id": "scene1",
     *     "title": "Living Room",
     *     "image": "/url/to/panorama1.jpg",
     *     "hotSpots": [
     *       {
     *         "pitch": 10,
     *         "yaw": 50,
     *         "type": "scene",
     *         "text": "Go to Kitchen",
     *         "sceneId": "scene2"
     *       }
     *     ]
     *   },
     *   {
     *     "id": "scene2",
     *     "title": "Kitchen",
     *     "image": "/url/to/panorama2.jpg",
     *     "hotSpots": []
     *   }
     * ]
     */
    _initMultiScene: function () {
        var scenes = {};
        var firstSceneId = "";

        try {
            var scenesArray = JSON.parse(this.scenesJson);
            if (!Array.isArray(scenesArray) || scenesArray.length === 0) {
                // Fall back to single scene mode
                this._initSingleScene();
                return;
            }

            firstSceneId = scenesArray[0].id || "scene0";

            scenesArray.forEach(function (scene, index) {
                var sceneId = scene.id || ("scene" + index);
                scenes[sceneId] = {
                    title: scene.title || ("Scene " + (index + 1)),
                    type: "equirectangular",
                    panorama: scene.image || scene.panorama || "",
                    hotSpots: (scene.hotSpots || []).map(function (hs) {
                        return {
                            pitch: hs.pitch || 0,
                            yaw: hs.yaw || 0,
                            type: hs.type || "info",
                            text: hs.text || "",
                            sceneId: hs.sceneId || undefined,
                            URL: hs.url || undefined,
                        };
                    }),
                };
            });
        } catch (e) {
            console.error("[360 View] Invalid scenes JSON:", e);
            this._initSingleScene();
            return;
        }

        this.viewer = window.pannellum.viewer(this.el, {
            default: {
                firstScene: firstSceneId,
                autoLoad: true,
                autoRotate: this.autoRotate ? -2 : 0,
                hfov: this.defaultFov,
                showZoomCtrl: true,
                showFullscreenCtrl: true,
            },
            scenes: scenes,
        });
    },

    /**
     * Bind the toggle button to switch between 360° and normal images.
     */
    _bindToggleButton: function () {
        var self = this;
        var toggleBtn = document.querySelector(".o_360_toggle_btn");
        if (!toggleBtn) return;

        toggleBtn.addEventListener("click", function () {
            var wrapper = document.querySelector(".o_360_viewer_wrapper");
            var normalImages = document.querySelector(".o_360_normal_images");
            var currentMode = toggleBtn.dataset.mode;

            if (currentMode === "360") {
                // Switch to normal images
                if (wrapper) wrapper.classList.add("d-none");
                if (normalImages) normalImages.classList.remove("d-none");
                toggleBtn.dataset.mode = "normal";
                toggleBtn.innerHTML = '<i class="fa fa-globe me-1"></i>Switch to 360° view';
                // Move button outside hidden wrapper
                if (normalImages && toggleBtn.parentElement) {
                    normalImages.parentElement.insertBefore(
                        toggleBtn.parentElement, normalImages.nextSibling
                    );
                }
            } else {
                // Switch back to 360°
                if (wrapper) wrapper.classList.remove("d-none");
                if (normalImages) normalImages.classList.add("d-none");
                toggleBtn.dataset.mode = "360";
                toggleBtn.innerHTML = '<i class="fa fa-image me-1"></i>Switch to normal images';
                // Resize viewer to fit (Pannellum needs this after visibility change)
                if (self.viewer) {
                    self.viewer.resize();
                }
            }
        });
    },

    /**
     * Show an error message if the viewer fails to initialize.
     */
    _showError: function () {
        this.el.innerHTML =
            '<div class="alert alert-warning text-center m-3">' +
            '<i class="fa fa-exclamation-triangle me-2"></i>' +
            "Unable to load 360° viewer. Please check the image." +
            "</div>";
    },

    /**
     * Cleanup when the widget is destroyed (page navigation).
     */
    destroy: function () {
        if (this.viewer) {
            try {
                this.viewer.destroy();
            } catch (e) {
                // Viewer might already be destroyed
            }
        }
        this._super.apply(this, arguments);
    },
});

export default publicWidget.registry.Website360Viewer;
