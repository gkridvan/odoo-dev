var APP_DATA = {
  "scenes": [
    {
      "id": "0-la-cuisine",
      "name": "la cuisine",
      "levels": [
        {
          "tileSize": 256,
          "size": 256,
          "fallbackOnly": true
        },
        {
          "tileSize": 512,
          "size": 512
        },
        {
          "tileSize": 512,
          "size": 1024
        },
        {
          "tileSize": 512,
          "size": 2048
        }
      ],
      "faceSize": 1520,
      "initialViewParameters": {
        "pitch": 0,
        "yaw": 0,
        "fov": 1.5707963267948966
      },
      "linkHotspots": [
        {
          "yaw": -0.45238687418143364,
          "pitch": -0.02562816594425854,
          "rotation": 0,
          "target": "0-la-cuisine"
        },
        {
          "yaw": -2.313363965982891,
          "pitch": 0.03435643372415953,
          "rotation": 0,
          "target": "1-la-rue"
        }
      ],
      "infoHotspots": []
    },
    {
      "id": "1-la-rue",
      "name": "la rue",
      "levels": [
        {
          "tileSize": 256,
          "size": 256,
          "fallbackOnly": true
        },
        {
          "tileSize": 512,
          "size": 512
        },
        {
          "tileSize": 512,
          "size": 1024
        },
        {
          "tileSize": 512,
          "size": 2048
        }
      ],
      "faceSize": 1520,
      "initialViewParameters": {
        "pitch": 0,
        "yaw": 0,
        "fov": 1.5707963267948966
      },
      "linkHotspots": [
        {
          "yaw": -2.9398195649195493,
          "pitch": 0.07310980897410602,
          "rotation": 0,
          "target": "0-la-cuisine"
        }
      ],
      "infoHotspots": [
        {
          "yaw": -0.9050311075038096,
          "pitch": 0.4490874805599159,
          "title": "Cour Petit",
          "text": "une rue assez calme"
        },
        {
          "yaw": -2.5547495880608793,
          "pitch": -0.05047146811888226,
          "title": "Maison",
          "text": "ma maison"
        }
      ]
    },
    {
      "id": "2-sal-de-bain",
      "name": "sal de bain",
      "levels": [
        {
          "tileSize": 256,
          "size": 256,
          "fallbackOnly": true
        },
        {
          "tileSize": 512,
          "size": 512
        },
        {
          "tileSize": 512,
          "size": 1024
        },
        {
          "tileSize": 512,
          "size": 2048
        }
      ],
      "faceSize": 1520,
      "initialViewParameters": {
        "pitch": 0,
        "yaw": 0,
        "fov": 1.5707963267948966
      },
      "linkHotspots": [
        {
          "yaw": 2.321407834938184,
          "pitch": 0.10100318607634229,
          "rotation": 0,
          "target": "0-la-cuisine"
        }
      ],
      "infoHotspots": [
        {
          "yaw": -2.534138776436791,
          "pitch": 0.673924741682189,
          "title": "Bordel no'1",
          "text": "Pardon pour le bordel"
        }
      ]
    }
  ],
  "name": "Project Title",
  "settings": {
    "mouseViewMode": "drag",
    "autorotateEnabled": true,
    "fullscreenButton": false,
    "viewControlButtons": false
  }
};
