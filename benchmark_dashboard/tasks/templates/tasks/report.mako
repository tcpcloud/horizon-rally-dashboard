
<%inherit file="base.mako"/>

<%block name="title_text">Benchmark Task Report</%block>

<%block name="media_queries">
    @media only screen and (min-width: 320px)  { .content-wrap { width:900px  } .content-main { width:600px } }
    @media only screen and (min-width: 900px)  { .content-wrap { width:880px  } .content-main { width:590px } }
    @media only screen and (min-width: 1000px) { .content-wrap { width:980px  } .content-main { width:690px } }
    @media only screen and (min-width: 1100px) { .content-wrap { width:1080px } .content-main { width:790px } }
    @media only screen and (min-width: 1200px) { .content-wrap { width:1180px } .content-main { width:890px } }
</%block>

<%block name="header_text">benchmark results</%block>

<%block name="content">
<script>
  var BenchmarkData = {
    source : ${source},
    data : ${data}
  };
</script>
<div ng-controller="BenchmarkController" ng-init="init()">
  <div id="RallyContent">
    <p id="page-error" class="notify-error" style="display:none"></p>

    <div id="content-nav" class="col-xs-2" ng-show="scenarios.length" ng-cloack>
      <div>
        <div class="nav-group"
             ng-class="{active:view.is_main}"
             ng-click="location.path('')">Benchmark overview</div>
        <div class="nav-group"
             ng-class="{active:view.is_source}"
             ng-click="location.path('source', '')">Input file</div>
      </div>
      <div>
        <div class="nav-group" title="{$n.cls$}"
             ng-repeat-start="n in nav track by $index"
             ng-click="showNav(n.idx)"
             ng-class="{expanded:n.idx==nav_idx}">
                <span ng-hide="n.idx==nav_idx">&#9658;</span>
                <span ng-show="n.idx==nav_idx">&#9660;</span>
                {$n.cls$} </div>
        <div class="nav-item" title="{$m.name$}"
             ng-show="n.idx==nav_idx"
             ng-class="{active:m.ref==scenario.ref}"
             ng-click="location.path(m.ref)"
             ng-repeat="m in n.met track by $index"
             ng-repeat-end>{$m.name$}</div>
      </div>
    </div>

    <div id="content-main" class="col-xs-10" ng-show="scenarios.length" ng-cloak>

      <div ng-show="view.is_main">
        <h1>Benchmark overview</h1>
        <table class="linked compact"
               ng-init="ov_srt='ref'; ov_dir=false">
          <thead>
            <tr>
              <th class="sortable"
                  title="Scenario name, with optional suffix of call number"
                  ng-click="ov_srt='ref'; ov_dir=!ov_dir">
                Scenario
                <span class="arrow">
                  <b ng-show="ov_srt=='ref' && !ov_dir">&#x25b4;</b>
                  <b ng-show="ov_srt=='ref' && ov_dir">&#x25be;</b>
                </span>
              <th class="sortable"
                  title="How long the scenario run, without context duration"
                  ng-click="ov_srt='load_duration'; ov_dir=!ov_dir">
                Load duration (s)
                <span class="arrow">
                  <b ng-show="ov_srt=='load_duration' && !ov_dir">&#x25b4;</b>
                  <b ng-show="ov_srt=='load_duration' && ov_dir">&#x25be;</b>
                </span>
              <th class="sortable"
                  title="Scenario duration plus context duration"
                  ng-click="ov_srt='full_duration'; ov_dir=!ov_dir">
                Full duration (s)
                <span class="arrow">
                  <b ng-show="ov_srt=='full_duration' && !ov_dir">&#x25b4;</b>
                  <b ng-show="ov_srt=='full_duration' && ov_dir">&#x25be;</b>
                </span>
              <th class="sortable"
                  title="Number of iterations"
                  ng-click="ov_srt='iterations_num'; ov_dir=!ov_dir">
                Iterations
                <span class="arrow">
                  <b ng-show="ov_srt=='iterations_num' && !ov_dir">&#x25b4;</b>
                  <b ng-show="ov_srt=='iterations_num' && ov_dir">&#x25be;</b>
                </span>
              <th class="sortable"
                  title="Scenario runner type"
                  ng-click="ov_srt='runner'; ov_dir=!ov_dir">
                Runner
                <span class="arrow">
                  <b ng-show="ov_srt=='runner' && !ov_dir">&#x25b4;</b>
                  <b ng-show="ov_srt=='runner' && ov_dir">&#x25be;</b>
                </span>
              <th class="sortable"
                  title="Number of errors occured"
                  ng-click="ov_srt='errors.length'; ov_dir=!ov_dir">
                Errors
                <span class="arrow">
                  <b ng-show="ov_srt=='errors.length' && !ov_dir">&#x25b4;</b>
                  <b ng-show="ov_srt=='errors.length' && ov_dir">&#x25be;</b>
                </span>
              <th class="sortable"
                  title="Whether SLA check is successful"
                  ng-click="ov_srt='sla_success'; ov_dir=!ov_dir">
                Success (SLA)
                <span class="arrow">
                  <b ng-show="ov_srt=='sla_success' && !ov_dir">&#x25b4;</b>
                  <b ng-show="ov_srt=='sla_success' && ov_dir">&#x25be;</b>
                </span>
            <tr>
          </thead>
          <tbody>
            <tr ng-repeat="sc in scenarios | orderBy:ov_srt:ov_dir"
                ng-click="location.path(sc.ref)">
              <td>{$sc.ref$}
              <td>{$sc.load_duration | number:3$}
              <td>{$sc.full_duration | number:3$}
              <td>{$sc.iterations_num$}
              <td>{$sc.runner$}
              <td>{$sc.errors.length$}
              <td>
                <span ng-show="sc.sla_success" class="status-pass">&#x2714;</span>
                <span ng-hide="sc.sla_success" class="status-fail">&#x2716;</span>
            <tr>
          </tbody>
        </table>
      </div>

      <div ng-show="view.is_source">
        <h1>Input file</h1>
        <pre class="code">{$source$}</pre>
      </div>

      <div ng-show="view.is_scenario">
        <h1>{$scenario.cls$}.<wbr>{$scenario.name$} ({$scenario.full_duration | number:3$}s)</h1>
        <ul class="tabs">
          <li ng-repeat="t in tabs"
              ng-show="t.isVisible()"
              ng-class="{active:t.id == tab}"
              ng-click="location.hash(t.id)">
            <div>{$t.name$}</div>
          </li>
          <div class="clearfix"></div>
        </ul>
        <div ng-include="tab"></div>

        <script type="text/ng-template" id="overview">
          {$ renderTotal() $}

          <p>
            Load duration: <b>{$scenario.load_duration | number:3$} s</b> &nbsp;
            Full duration: <b>{$scenario.full_duration | number:3$} s</b> &nbsp;
            Iterations: <b>{$scenario.iterations_num$}</b> &nbsp;
            Failures: <b>{$scenario.errors.length$}</b>
          </p>

          <div ng-show="scenario.sla.length">
            <h2>Service-level agreement</h2>
            <table class="striped">
              <thead>
                <tr>
                  <th>Criterion
                  <th>Detail
                  <th>Success
                <tr>
              </thead>
              <tbody>
                <tr class="rich"
                    ng-repeat="row in scenario.sla track by $index"
                    ng-class="{'status-fail':!row.success, 'status-pass':row.success}">
                  <td>{$row.criterion$}
                  <td>{$row.detail$}
                  <td class="capitalize">{$row.success$}
                <tr>
              </tbody>
            </table>
          </div>

          <h2>Total durations</h2>
          <table class="striped">
            <thead>
              <tr>
                <th ng-repeat="i in scenario.table_cols track by $index">{$i$}
              <tr>
            </thead>
            <tbody>
              <tr ng-class="{richcolor:$last}"
                  ng-repeat="row in scenario.table_rows track by $index">
                <td ng-repeat="i in row track by $index">{$i$}
              <tr>
            </tbody>
          </table>

          <h2>Charts for the Total durations</h2>
          <div class="chart">
            <svg id="total-stack"></svg>
          </div>

          <div class="chart lesser top-margin">
            <svg id="total-pie"></svg>
          </div>

          <div class="chart larger top-margin"
               ng-show="scenario.iterations.histogram.length">
            <svg id="total-histogram"></svg>
            <select class="chart-dropdown"
                    ng-model="totalHistogramModel"
                    ng-options="i.label for i in histogramOptions"></select>
          </div>
        </script>

        <script type="text/ng-template" id="details">
          {$renderDetails()$}

          <h2>Charts for each Atomic Action</h2>
          <div class="chart">
            <svg id="atomic-stack"></svg>
          </div>

          <div class="chart lesser top-margin">
            <svg id="atomic-pie"></svg>
          </div>

          <div class="chart larger top-margin"
               ng-show="scenario.atomic.histogram.length">
            <svg id="atomic-histogram"></svg>
            <select class="chart-dropdown"
                    ng-model="atomicHistogramModel"
                    ng-options="i.label for i in histogramOptions"></select>
          </div>
        </script>

        <script type="text/ng-template" id="output">
          {$renderOutput()$}

          <h2>Scenario output</h2>
          <div class="chart">
            <svg id="output-stack"></svg>
          </div>
        </script>

        <script type="text/ng-template" id="failures">
          <h2>Benchmark failures (<ng-pluralize
            count="scenario.errors.length"
            when="{'1': '1 iteration', 'other': '{} iterations'}"></ng-pluralize> failed)
          </h2>
          <table class="striped">
            <thead>
              <tr>
                <th>
                <th>Iteration
                <th>Exception type
                <th>Exception message
              </tr>
            </thead>
            <tbody>
              <tr class="expandable"
                  ng-repeat-start="i in scenario.errors track by $index"
                  ng-click="i.expanded = ! i.expanded">
                <td>
                  <span ng-hide="i.expanded">&#9658;</span>
                  <span ng-show="i.expanded">&#9660;</span>
                <td>{$i.iteration$}
                <td>{$i.type$}
                <td class="failure-mesg">{$i.message$}
              </tr>
              <tr ng-show="i.expanded" ng-repeat-end>
                <td colspan="4" class="failure-trace">{$i.traceback$}
              </tr>
            </tbody>
          </table>
        </script>

        <script type="text/ng-template" id="task">
          <h2>Scenario Configuration</h2>
          <pre class="code">{$scenario.config$}</pre>
        </script>
      </div>

    </div>
    <div class="clearfix"></div>
    </div>
    </div>
</%block>

<%block name="js_after">
    if (! window.angular) {(function(f){
      f(document.getElementById("content-nav"), "none");
      f(document.getElementById("content-main"), "none");
      f(document.getElementById("page-error"), "block").textContent = "Failed to load AngularJS framework"
    })(function(e, s){e.style.display = s; return e})}
</%block>