 /* Initialization */
angular.module("rally-benchmark",[]).
controller("BenchmarkController",["$scope","$location",function($scope,$location){
	  $scope.source = BenchmarkData.source;
      $scope.scenarios = BenchmarkData.data;
      $scope.location = {
        /* This is a junior brother of angular's $location, that allows non-`#'
           symbol in uri, like `#/path/hash' instead of `#/path#hash' */
        _splitter: "/",
        normalize: function(str) {
          /* Remove unwanted characters from string */
          if (typeof str !== "string") { return "" }
          return str.replace(/[^\w\-\.]/g, "")
        },
        _parseUri: function(uriStr) {
          /* :returns: {path:string, hash:string} */
          var self = this;
          var obj = {path: "", hash: ""};
          angular.forEach(uriStr.split(self._splitter), function(v){
            var s = self.normalize(v);
            if (! s) { return }
            if (! this.path) { this.path = s } else if (! this.hash) { this.hash = s }
          }, obj)
          return obj
        },
        uri: function(obj) {
          /* Getter/Setter */
          if (! obj) { return this._parseUri($location.url()) }
          if (obj.path && obj.hash) {
            $location.url(obj.path + this._splitter + obj.hash)
          } else if (obj.path) {
            $location.url(obj.path)
          } else {
            $location.url("/")
          }
        },
        path: function(path, hash) {
          /* Getter/Setter */
          var uri = this.uri();
          if (path === "") { return this.uri({}) }
          path = this.normalize(path);
          if (! path) { return uri.path }
          uri.path = path;
          var _hash = this.normalize(hash);
          if (_hash || hash === "") { uri.hash = _hash }
          return this.uri(uri)
        },
        hash: function(hash) {
          /* Getter/Setter */
          var uri = this.uri();
          if (! hash) { return uri.hash }
          return this.uri({path:uri.path, hash:hash})
        }
      }

      /* Dispatch */

      $scope.route = function(uri) {
        if (! $scope.scenarios) {
          return
        }
        if (uri.path in $scope.scenarios_map) {
          $scope.view = {is_scenario:true};
          $scope.scenario = $scope.scenarios_map[uri.path];
          $scope.nav_idx = $scope.nav_map[uri.path];
          $scope.showTab(uri.hash);
        } else {
          $scope.scenario = undefined
          if (uri.path === "source") {
            $scope.view = {is_source:true}
          } else {
            $scope.view = {is_main:true}
          }
        }
      }

      $scope.$on("$locationChangeSuccess", function (event, newUrl, oldUrl) {
        $scope.route($scope.location.uri())
      });

      /* Navigation */

      $scope.showNav  = function(nav_idx) {
        $scope.nav_idx = nav_idx
      }

      /* Tabs */

      $scope.tabs = [
        {
          id: "overview",
          name: "Overview",
          visible: function(){ return !! $scope.scenario.iterations.pie.length }
        },{
          id: "details",
          name: "Details",
          visible: function(){ return !! $scope.scenario.atomic.pie.length }
        },{
          id: "output",
          name: "Output",
          visible: function(){ return !! $scope.scenario.output.length }
        },{
          id: "failures",
          name: "Failures",
          visible: function(){ return !! $scope.scenario.errors.length }
        },{
          id: "task",
          name: "Input task",
          visible: function(){ return !! $scope.scenario.config }
        }
      ];
      $scope.tabs_map = {};
      angular.forEach($scope.tabs,
                      function(tab){ this[tab.id] = tab }, $scope.tabs_map);

      $scope.showTab = function(tab_id) {
        $scope.tab = tab_id in $scope.tabs_map ? tab_id : "overview"
      }

      for (var i in $scope.tabs) {
        if ($scope.tabs[i].id === $scope.location.hash()) {
          $scope.tab = $scope.tabs[i].id
        }
        $scope.tabs[i].isVisible = function(){
          if ($scope.scenario) {
            if (this.visible()) {
              return true
            }
            /* If tab should be hidden but is selected - show another one */
            if (this.id === $scope.location.hash()) {
              for (var i in $scope.tabs) {
                var tab = $scope.tabs[i];
                if (tab.id != this.id && tab.visible()) {
                  $scope.tab = tab.id;
                  return false
                }
              }
            }
          }
          return false
        }
      }

      /* Charts */

      var Charts = {
        _render: function(selector, datum, chart){
          nv.addGraph(function() {
            d3.select(selector)
              .datum(datum)
              .transition()
              .duration(0)
              .call(chart);
            nv.utils.windowResize(chart.update)
          })
        },
        pie: function(selector, datum){
          var chart = nv.models.pieChart()
            .x(function(d) { return d.key })
            .y(function(d) { return d.value })
            .showLabels(true)
            .labelType("percent")
            .donut(true)
            .donutRatio(0.25)
            .donutLabelsOutside(true);
            this._render(selector, datum, chart)
        },
        stack: function(selector, datum){
          var chart = nv.models.stackedAreaChart()
            .x(function(d) { return d[0] })
            .y(function(d) { return d[1] })
            .useInteractiveGuideline(true)
            .clipEdge(true);
          chart.xAxis
            .axisLabel("Iteration (order number of method's call)")
            .showMaxMin(false)
            .tickFormat(d3.format("d"));
          chart.yAxis
            .axisLabel("Duration (seconds)")
            .tickFormat(d3.format(",.2f"));
          this._render(selector, datum, chart)
        },
        histogram: function(selector, datum){
          var chart = nv.models.multiBarChart()
            .reduceXTicks(true)
            .showControls(false)
            .transitionDuration(0)
            .groupSpacing(0.05);
          chart.legend
            .radioButtonMode(true)
          chart.xAxis
            .axisLabel("Duration (seconds)")
            .tickFormat(d3.format(",.2f"));
          chart.yAxis
            .axisLabel("Iterations (frequency)")
            .tickFormat(d3.format("d"));
          this._render(selector, datum, chart)
        }
      };

      $scope.renderTotal = function() {
        if (! $scope.scenario) {
          return
        }
        Charts.stack("#total-stack", $scope.scenario.iterations.iter);
        Charts.pie("#total-pie", $scope.scenario.iterations.pie);

        if ($scope.scenario.iterations.histogram.length) {
          var idx = this.totalHistogramModel.value;
          Charts.histogram("#total-histogram",
                           [$scope.scenario.iterations.histogram[idx]])
        }
      }

      $scope.renderDetails = function() {
        if (! $scope.scenario) {
          return
        }
        Charts.stack("#atomic-stack", $scope.scenario.atomic.iter);
        Charts.pie("#atomic-pie", $scope.scenario.atomic.pie);
        if ($scope.scenario.atomic.histogram.length) {
          var atomic = [];
          var idx = this.atomicHistogramModel.value;
          for (var i in $scope.scenario.atomic.histogram) {
            atomic[i] = $scope.scenario.atomic.histogram[i][idx]
          }
          Charts.histogram("#atomic-histogram", atomic)
        }
      }

      $scope.renderOutput = function() {
        if ($scope.scenario) {
          Charts.stack("#output-stack", $scope.scenario.output)
        }
      };

      $scope.showError = function(message) {
          return (function (e) {
            e.style.display = "block";
            e.textContent = message
          })(document.getElementById("page-error"))
      }

      $scope.init = function(){
          if (! $scope.scenarios.length) {
            return $scope.showError("Benchmark has empty scenarios data")
          }
          $scope.histogramOptions = [];
          $scope.totalHistogramModel = {label:'', value:0};
          $scope.atomicHistogramModel = {label:'', value:0};

          /* Compose data mapping */

          $scope.nav = [];
          $scope.nav_map = {};
          $scope.scenarios_map = {};
          var scenario_ref = $scope.location.path();
          var met = [];
          var itr = 0;
          var cls_idx = 0;
          var prev_cls, prev_met;

          for (var idx in $scope.scenarios) {
            var sc = $scope.scenarios[idx];
            if (! prev_cls) {
              prev_cls = sc.cls
            }
            else if (prev_cls !== sc.cls) {
              $scope.nav.push({cls:prev_cls, met:met, idx:cls_idx});
              prev_cls = sc.cls;
              met = [];
              itr = 1;
              cls_idx += 1
            }

            if (prev_met !== sc.met) {
              itr = 1
            }

            sc.ref = $scope.location.normalize(sc.cls+"."+sc.met+(itr > 1 ? "-"+itr : ""));
            $scope.scenarios_map[sc.ref] = sc;
            $scope.nav_map[sc.ref] = cls_idx;
            var current_ref = $scope.location.path();
            if (sc.ref === current_ref) {
              scenario_ref = sc.ref
            }

            met.push({name:sc.name, itr:itr, idx:idx, ref:sc.ref});
            prev_met = sc.met;
            itr += 1

            /* Compose histograms options, from first suitable scenario */

            if (! $scope.histogramOptions.length && sc.iterations.histogram) {
              for (var i in sc.iterations.histogram) {
                $scope.histogramOptions.push({
                  label: sc.iterations.histogram[i].method,
                  value: i
                })
              }
              $scope.totalHistogramModel = $scope.histogramOptions[0];
              $scope.atomicHistogramModel = $scope.histogramOptions[0];
            }
          }

          if (met.length) {
            $scope.nav.push({cls:prev_cls, met:met, idx:cls_idx})
          }

          /* Start */

          var uri = $scope.location.uri();
          uri.path = scenario_ref;
          $scope.route(uri);
      };

}]);