var app = angular.module('ezreg');
app.requires.push('ngTable');
app.controller('RefundsController', ['$scope','$http','growl',"DRFNgTableParams", RefundsController]);

function RefundsController($scope,$http,growl,DRFNgTableParams) {
	var defaults={};
	$scope.status_choices = [{id:'pending',title:'Pending'},{id:'cancelled',title:'Cancelled'},{id:'completed',title:'Completed'}];
	$scope.init = function(params){
	    $scope.params = params;
        $scope.filters = params.filters;
        $scope.tableParams = DRFNgTableParams('/api/refunds/',{sorting: { requested: "desc" },filter:$scope.filters});
        $scope.$watchCollection('filters', function(newFilters, oldFilters) {
            angular.extend($scope.tableParams.filter(), newFilters);
        });
	};
	$scope.registrationLink = function(registration){return django_js_utils.urls.resolve('registration', { id: registration })};
 	$scope.eventLink = function(event){return django_js_utils.urls.resolve('manage_event', { event: event })};
	$scope.complete = function (refund) {
	   if (confirm('Are you sure you want to complete this refund?  This action cannot be undone.')){
    		$http.post('/api/refunds/'+refund.id+'/complete/',{}).then(function(response){
    			growl.success('Refund set as completed' ,{ttl: 5000});
    			$scope.tableParams.reload();
    	  	}, function(response){
    			if (response.data.detail)
    				growl.error(response.data.detail ,{ttl: 5000});
    		});
	    }
	  };
	$scope.cancel = function (refund) {
       if (confirm('Are you sure you want to cancel this refund?  This action cannot be undone.')){ 
            $http.post('/api/refunds/'+refund.id+'/cancel/',{}).then(function(response){
                growl.success('Refund cancelled' ,{ttl: 5000});
                $scope.tableParams.reload();
            }, function(response){
                if (response.data.detail)
                    growl.error(response.data.detail ,{ttl: 5000});
            });
        }
      };
//	$scope.tableParams = DRFNgTableParams('/api/emails/',{sorting: { last_attempt: "desc" }});
}


