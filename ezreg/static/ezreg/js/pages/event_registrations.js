var app = angular.module('ezreg');
app.requires.push('ngTable');
app.controller('RegistrationController', ['$scope','$http','$modal','growl','Registration',"NgTableParams", RegistrationController])

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

function RegistrationController($scope,$http,$modal,growl,Registration,NgTableParams) {
	var defaults={};
	console.log('wtf');
	var create_filter_choices = function(choices){
		filter_choices = [];
		for(var id in choices)
			filter_choices.push({id:id,title:choices[id]});
		console.log(filter_choices);
		return filter_choices;
	};
	$scope.init = function(id,statuses,processors,payment_statuses){
		$scope.checked={};
		$scope.statuses = statuses;
		$scope.payment_statuses = payment_statuses;
		$scope.statuses_filter_choices = create_filter_choices(statuses);
		$scope.processors_filter_choices = create_filter_choices(processors);
		$scope.payment_status_filter_choices = create_filter_choices(payment_statuses);
		$scope.id = id;
	};
	$scope.registrationLink = function(registration){return django_js_utils.urls.resolve('registration', { id: registration.id })};
	$scope.modifyRegistrationLink = function(registration){return django_js_utils.urls.resolve('modify_registration', { id: registration.id })};
	$scope.updateRegistrationStatusLink = function(registration){return django_js_utils.urls.resolve('update_registration_status', { id: registration.id })};
	
	$scope.selectAll = function(){
		if ($scope.select_all)
			$http.get('/api/registrations/',{params:$scope.registrationParameters}).then(function(response){
		  		console.log(response.data);
		  		$scope.checked = {}
		  		angular.forEach(response.data.results,function(registration,index){
		  			$scope.checked[registration.id]=true;
		  		});
		  		
		  	});
		else
			$scope.checked = {};
	}
	
//	var registrations = Registration.query({event: '2Z89K20AZ3'});
	$scope.tableParams = new NgTableParams({
//	      page: 1, // show first page
	      count: 10 // count per page
	    }, {
	      filterDelay: 0,
//	      dataset: registrations
		  	getData: function(params) {
		  		var url = params.url();
		  	var query_params = {event:$scope.id,test:'False',page:url.page,page_size:url.count,ordering:params.orderBy().join(',').replace('+','')};
		  	angular.extend(query_params, params.filter());
	        // ajax request to api
		  	$scope.registrationParameters = angular.copy(query_params);
		  	angular.extend($scope.registrationParameters, {page_size:10000,page:1});
		  	return $http.get('/api/registrations/',{params:query_params}).then(function(response){
		  		params.total(response.data.count);
		  		return response.data.results;
		  	});
//	        return Registration.query({event: '2Z89K20AZ3',page_size:3}).$promise.then(function(data) {
//	          console.log(data,data.length);
////	          params.total(data.count); // recal. page nav controls
//	          return data;
//	        });
	      }
	    });
//	getData: function(params) {
//        // ajax request to api
//        return Registration.query({event: '2Z89K20AZ3').$promise.then(function(data) {
//          params.total(data.inlineCount); // recal. page nav controls
//          return data.results;
//        });
//      }
		$scope.getSelected = function(){
			var ids = [];
			angular.forEach($scope.checked,function(value,key){
				if (value)
					ids.push(key);
			});
			return ids;
		}
		$scope.update_statuses_old = function(){
			console.log($scope.getSelected());
		};
		
		$scope.export_registrations = function(){
			var modalInstance = $modal.open({
			      animation: $scope.animationsEnabled,
			      templateUrl: 'exportRegistrations.html',
			      controller: 'exportCtrl',
			      size: 'lg',
			      resolve: {
			        selected: function () {
			          return $scope.getSelected();
			        },
			        event_id: function () {
			          return $scope.id;
			        }
			      }
			    });

			    modalInstance.result.then(function () {
			    	console.log('exported');
			    }, function () {
			      $log.info('Modal dismissed at: ' + new Date());
			    });
		};
		
		
		$scope.update_statuses = function () {

		    var modalInstance = $modal.open({
		      animation: $scope.animationsEnabled,
		      templateUrl: 'updateStatus.html',
		      controller: 'updateStatusCtrl',
		      size: 'lg',
		      resolve: {
		        selected: function () {
		          return $scope.getSelected();
		        },
		        event_id: function () {
		          return $scope.id;
		        }
		      }
		    });

		    modalInstance.result.then(function () {
		    	console.log('refresh');
		    	$scope.tableParams.reload();
		    }, function () {
		      $log.info('Modal dismissed at: ' + new Date());
		    });
		  };
}


app.controller('updateStatusCtrl', function ($scope, $http, growl, $modalInstance, event_id, selected) {

	  $scope.params = {selected:selected};

	  $scope.update_statuses = function () {
		var url = django_js_utils.urls.resolve('update_event_statuses', { event: event_id });
		$http.post(url,$scope.params).then(function(response){
			$modalInstance.close($scope.params.selected);
	  	}, function(response){
			if (response.data.detail)
				growl.error(response.data.detail ,{ttl: 5000});
		}
		);
	    
	  };

	  $scope.cancel = function () {
	    $modalInstance.dismiss('cancel');
	  };
	});
app.controller('exportCtrl', function ($scope, $http, growl, $modalInstance, event_id, selected) {

	  $scope.selected = selected;

	  $scope.update_statuses = function () {
		var url = django_js_utils.urls.resolve('export_registrations', { event: event_id });
		$http.post(url,$scope.params).then(function(response){
			$modalInstance.close($scope.params.selected);
	  	}, function(response){
			if (response.data.detail)
				growl.error(response.data.detail ,{ttl: 5000});
		});
	    
	  };
	  $scope.export_registrations = function (){
		  $('#exportForm').submit();
		  $modalInstance.close();
	  };
	  $scope.cancel = function () {
	    $modalInstance.dismiss('cancel');
	  };
	});