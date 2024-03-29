var app = angular.module('ezreg');
app.requires.push('ngTable');
app.controller('EventEmailsController', ['$scope','$http','growl',"NgTableParams", EventEmailsController])

function EventEmailsController($scope,$http,growl,NgTableParams) {
	var defaults={};
	$scope.sent_choices = [{id:'False',title:'Failed'},{id:'True',title:'Sent'}];
	$scope.init = function(event_id){
		$scope.checked={};
		$scope.event_id = event_id;
	};
	$scope.registrationLink = function(registration){return django_js_utils.urls.resolve('registration', { id: registration })};
	$scope.send_event_emails = function (selected) {
		var url = django_js_utils.urls.resolve('send_event_emails', { event: $scope.event_id });
		$http.post(url,{selected:selected}).then(function(response){
			growl.success('Unsent emails sent' ,{ttl: 5000});
			$scope.tableParams.reload();
	  	}, function(response){
			if (response.data.detail)
				growl.error(response.data.detail ,{ttl: 5000});
		});
	    
	  };
	
//	$scope.tableParams = DRFNgTableParams('/api/emails/',{sorting: { last_attempt: "desc" }});
	$scope.tableParams = new NgTableParams({
//	      page: 1, // show first page
		  sorting: { 'last_attempt': 'desc'},
	      count: 10 // count per page
	    }, {
	      filterDelay: 0,
		  	getData: function(params) {
		  		var url = params.url();
		  	var query_params = {registrations__event:$scope.event_id,page:url.page,page_size:url.count,ordering:params.orderBy().join(',').replace('+','')};
		  	angular.extend(query_params, params.filter());
	        // ajax request to api
		  	return $http.get('/api/emails/',{params:query_params}).then(function(response){
		  		params.total(response.data.count);
		  		return response.data.results;
		  	});
	      }
	    });
		$scope.getSelected = function(){
			var selection = [];
			angular.forEach($scope.checked,function(value,key){
				if (value)
					selection.push(key);
			});
			return selection;
		}
}


