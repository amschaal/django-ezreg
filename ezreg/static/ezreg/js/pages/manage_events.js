var app = angular.module('ezreg');
app.requires.push('ngTable');
app.controller('EventsController', ['$scope','$http','NgTableParams', EventsController]);

/*
app.config(setConfigPhaseSettings);
setConfigPhaseSettings.$inject = ["ngTableFilterConfigProvider"];
function setConfigPhaseSettings(ngTableFilterConfigProvider) {
    var filterAliasUrls = {
      "checkbox": "checkbox_filter.html",
      "sent": "checkbox_filter.html"
    };
    ngTableFilterConfigProvider.setConfig({
      aliasUrls: filterAliasUrls
    });

//    // optionally set a default url to resolve alias names that have not been explicitly registered
//    // if you don't set one, then 'ng-table/filters/' will be used by default
//    ngTableFilterConfigProvider.setConfig({
//      defaultBaseUrl: "ng-table/filters/"
//    });

  }
*/

function EventsController($scope,$http,NgTableParams) {
	$scope.init = function(id,statuses,processors,payment_statuses){
		$http.get('/api/events/',{}).then(function(response){
		  		console.log(response.data);
		  		$scope.tableParams = new NgTableParams({},{dataset:response.data.results});
			}
		);
	};
};
