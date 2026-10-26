# Web applications

Interactive GeoDevelopment apps for Cambodia. Most are built on Google Earth Engine (GEE) and run in the browser.

| App | Launch | Source |
| --- | --- | --- |
| Localized dynamics of luminosity-based GDP | [egdp-dynamics-cambodia](https://carlos-mendez.projects.earthengine.app/view/egdp-dynamics-cambodia) | [`egdp-dynamics-cambodia.js`](egdp-dynamics-cambodia.js) · [GEE code editor](https://code.earthengine.google.com/5600cd685ba72015d770d685b7676dd1?hideCode=true) |
| Comparative regional dynamics of luminosity-based GDP | [space-time-dynamics-egdp-cambodia](https://carlos-mendez.projects.earthengine.app/view/space-time-dynamics-egdp-cambodia) | [GEE code editor](https://code.earthengine.google.com/3dee778f1c961375c1882082aad33f32?hideCode=true) |
| Land surface temperature, soil moisture and land cover | [lst-smc-byregion](https://ee-yukietohjaxa.projects.earthengine.app/view/lst-smc-byregion) | External (GEE app) |
| Poverty mapping dashboard | [cambodiapovertymapping.sig-gis.com](https://cambodiapovertymapping.sig-gis.com/en/map/) | External (Spatial Informatics Group) · [About](https://cambodiapovertymapping.sig-gis.com/en/home/) |

## Using the GEE source

1. Open the [Earth Engine code editor](https://code.earthengine.google.com/).
2. Paste the contents of a `.js` file into a new script and press **Run**.

`egdp-dynamics-cambodia.js` adapts Jeff Howarth's (Middlebury College) *lights-change-time-neighborhood* app to Cambodia. It uses the gridded electricity-consumption-based GDP of Chen et al. (2022) from the `projects/sat-io/open-datasets/GRIDDED_EC-GDP` community catalog.
