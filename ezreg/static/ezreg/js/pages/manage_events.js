var app = angular.module('ezreg');
app.requires.push('ngTable');
app.controller('EventsController', ['$scope','DRFNgTableParams', EventsController]);

function EventsController($scope,DRFNgTableParams) {
	$scope.init = function(id,statuses,processors,payment_statuses){
		$scope.filters = {active: 'True'};
		$scope.tableParams = DRFNgTableParams('/api/events/',{sorting: { start_time: "desc" },filter:$scope.filters});
		$scope.$watchCollection('filters', function(newFilters, oldFilters) {
			angular.extend($scope.tableParams.filter(), newFilters);
		});
//		$scope.changeFilter = function(field, value){
//		      var filter = {};
//		      filter[field] = value;
//		      angular.extend($scope.tableParams.filter(), filter);
//		    }
	};
};
