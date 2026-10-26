// How conditions change across time within different neighborhoods of a point of interest
// Original source: https://jhowarth.users.earthengine.app/view/lights-change-time-neighborhood
// Version: -20250829 (Improved for Cambodia focus)

// ======================
// Define style variables
// ======================

var background = '#211F10';

// ===========================================
// Define a default Point of Interest and Map Center
// ===========================================

// Set the default location to Phnom Penh, Cambodia.
var defaultPoint = ee.Geometry.Point(104.9282, 11.5564);

// Set the initial map view to focus on Cambodia.
var mapCenter = {lon: 104.9, lat: 12.5, zoom: 7};

// ===========
// Compose map
// ===========

// Initialize map
var map = ui.Map(mapCenter);

// Set base map to hybrid satellite/map view
map.setOptions('HYBRID');

// Import and filter the luminosity-based GDP dataset for 2000-2019
var lights = ee.ImageCollection("projects/sat-io/open-datasets/GRIDDED_EC-GDP")
             .filterDate('2000-01-01', '2020-01-01')
             .select('b1');

// Define visualization parameters for the GDP layer
var lightsVis = {min: 0, max: 15, palette:['black', 'purple', 'orange', 'yellow', 'white']};

// Add the maximum GDP value over the time period as a layer
map.addLayer(lights.max(), lightsVis, 'Max GDP (2000-2019)');

// ================================
// Compose side panel for information and chart
// ================================

// Initialize side panel
var panelSide = ui.Panel({
  style: {
    width: '30%',
    backgroundColor: background
  }
});

// Compose title
var title = ui.Label({
  value: 'Economic Growth in Cambodia: A View from Space',
  style: {
    fontSize: '28px',
    fontWeight: 'bold',
    fontFamily: 'Helvetica',
    color: 'yellow',
    padding: '8px',
    backgroundColor: background
  }
});

// Explain how the chart works
var chartInstructions = ui.Label({
  value: "CLICK anywhere on the map to generate a chart. The chart below shows how luminosity-based GDP has changed over time at three different spatial scales around the selected point. The app starts by showing data for Phnom Penh.",
  style: {
    fontSize: '18px',
    fontFamily: 'Helvetica',
    color: 'white',
    padding: '8px',
    backgroundColor: background
  }
});

// Explain how to explore the map
var useInstructions = ui.Label({
  value: "If you zoom in, you will see three circles around the red dot: 1 km (yellow), 5 km (orange), and 10 km (red). You can also use the search bar at the top to find other places.",
  style: {
    fontSize: '18px',
    fontFamily: 'Helvetica',
    color: 'white',
    padding: '8px',
    backgroundColor: background
  }
});

// Create panel to hold the chart
var chartPanel = ui.Panel({
  style: {
    backgroundColor: background
  }
});

// Add data source credit
var sources = ui.Label({
  value: 'Data source: Chen et al. (2022). Global 1 km× 1 km gridded revised real gross domestic product... Scientific Data, 9(1), 1-14.',
  style: {
    fontSize: '11px',
    fontFamily: 'Helvetica',
    color: 'white',
    padding: '8px',
    backgroundColor: background
  }
});

// Add author credit
var credit = ui.Label({
  value: 'Visualization code: Jeff Howarth (Middlebury College) & Carlos Mendez (Nagoya University)',
  style: {
    fontSize: '11px',
    fontFamily: 'Helvetica',
    color: 'white',
    padding: '8px',
    backgroundColor: background
  }
});

// =============================================
// Initialize split panel for main layout
// =============================================

// Create the split panel with the side panel and the map
var splitPanel = ui.SplitPanel({
  firstPanel: panelSide,
  secondPanel: map,
});

// Clear root and add the new split panel layout
ui.root.clear();
ui.root.add(splitPanel);

// Add widgets to the side panel in order
panelSide.add(title);
panelSide.add(chartInstructions);
panelSide.add(chartPanel);
panelSide.add(useInstructions);
panelSide.add(sources);
panelSide.add(credit);

// ======================
// Define core functions
// ======================

// Function to create buffered regions around a point
var makeRegions = function(point) {
  var scale1 = 1000; // 1 km
  var scale2 = 5000; // 5 km
  var scale3 = 10000; // 10 km
  var regions = ee.FeatureCollection(ee.Feature(point.buffer(scale1)).set('scale', scale1))
          .merge(ee.FeatureCollection(ee.Feature(point.buffer(scale2)).set('scale', scale2)))
          .merge(ee.FeatureCollection(ee.Feature(point.buffer(scale3)).set('scale', scale3)));
  return regions;
};

// Function to display the point and buffer regions on the map
function showRegionsOnMap(point) {
  var dot = ui.Map.Layer(point, {color: 'FF0000'}, 'Point of Interest'); // Red dot
  var regions = makeRegions(point);
  var region1 = ui.Map.Layer(regions.filter(ee.Filter.eq('scale', 1000)), {color: 'FFFF00'}, '1 km'); // Yellow
  var region2 = ui.Map.Layer(regions.filter(ee.Filter.eq('scale', 5000)), {color: 'FFA500'}, '5 km'); // Orange
  var region3 = ui.Map.Layer(regions.filter(ee.Filter.eq('scale', 10000)), {color: 'FF0000'}, '10 km'); // Red

  // Using set() replaces layers at that index, preventing layer buildup on multiple clicks
  map.layers().set(1, region3);
  map.layers().set(2, region2);
  map.layers().set(3, region1);
  map.layers().set(4, dot);
}

// Function to generate and display the time-series chart
function makeChart(point) {
  var regions = makeRegions(point);
  var chart = ui.Chart.image.seriesByRegion({
      imageCollection: lights,
      regions: regions,
      reducer: ee.Reducer.median(), // Use median to reduce outlier effects
      scale: 1000,
      seriesProperty: 'scale'
  }).setOptions({
    title: 'Luminosity-based GDP Over Time',
    titleTextStyle: {color: 'yellow', fontSize: 16},
    backgroundColor: {fill: background},
    series: {
      0: {color: 'yellow', curveType: 'function', labelInLegend: '1 Km Radius'},
      1: {color: 'orange', curveType: 'function', labelInLegend: '5 Km Radius'},
      2: {color: 'red', curveType: 'function', labelInLegend: '10 Km Radius'}
    },
    vAxis: {
      title: 'GDP (Millions of 2017 USD)',
      textStyle: {color: 'white', fontSize: 12},
      gridlines: {color: 'gray'}
    },
    hAxis: {
      title: 'Date',
      format: 'yyyy',
      gridlines: {color: 'gray'},
      textStyle: {color: 'white', fontSize: 12}
    },
    legend: {
      textStyle: {color: 'white', fontSize: 12}
    }
  });
  chartPanel.clear();
  chartPanel.add(chart);
}

// =============================================
// Interactivity and Initialization
// =============================================

// Define what happens when the user clicks the map
map.onClick(function(coordinates){
  var point = ee.Geometry.Point([coordinates.lon, coordinates.lat]);
  showRegionsOnMap(point);
  makeChart(point);
  map.centerObject(point, 10); // Center map on clicked point with a closer zoom
});

// Initialize the app with the default location (Phnom Penh)
showRegionsOnMap(defaultPoint);
makeChart(defaultPoint);
