var app = angular.module('ezreg');
app.requires.push('ngTable');
app.controller('EventsController', ['$scope','DRFNgTableParams', EventsController]);

function EventsController($scope,DRFNgTableParams) {
	$scope.init = function(id,statuses,processors,payment_statuses){
		$scope.tableParams = DRFNgTableParams('/api/events/',{sorting: { start_date: "desc" }});
	};
};
