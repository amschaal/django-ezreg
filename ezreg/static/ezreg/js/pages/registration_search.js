var app = angular.module('ezreg');
app.requires.push('ngTable');
app.controller('RegistrationSearchController', ['$scope','$filter','$http',"NgTableParams",'$httpParamSerializer', RegistrationSearchController])

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

function RegistrationSearchController($scope,$filter,$http,NgTableParams,$httpParamSerializer) {
	var defaults={};
	$scope.filters={};
	var create_filter_choices = function(choices){
		filter_choices = [];
		for(var id in choices)
			filter_choices.push({id:id,title:choices[id]});
		console.log(filter_choices);
		return filter_choices;
	};
	$scope.init = function(statuses,payment_statuses){
		$scope.statuses = statuses;
		$scope.payment_statuses = payment_statuses;
		$scope.statuses_filter_choices = create_filter_choices(statuses);
		$scope.payment_status_filter_choices = create_filter_choices(payment_statuses);
	};
	$scope.updateFilter = function(){
		var lte = $filter('date')($scope.filters.end_date, 'yyyy-MM-dd');
		var gte = $filter('date')($scope.filters.start_date, 'yyyy-MM-dd');
		var filters = {
				registered__lte: lte?lte+'T00:00:00':null,
				registered__gte: gte?gte+'T00:00:00':null,
		}
		angular.extend($scope.tableParams.filter(), filters);
//		$scope.tableParams.filter(angular.copy($scope.registrationParameters));
	}
	$scope.tableParams = new NgTableParams({
//	      page: 1, // show first page
		  sorting: { 'registered': 'desc'},
	      count: 10 // count per page
	    }, {
	      filterDelay: 0,
		  	getData: function(params) {
		  		var url = params.url();
		  	var query_params = {test:'False',page:url.page,page_size:url.count,ordering:params.orderBy().join(',').replace('+','')};
		  	angular.extend(query_params, params.filter());
	        // ajax request to api
		  	$scope.registrationParameters = angular.copy(query_params);
		  	angular.extend($scope.registrationParameters, {page_size:10000,page:1});
		  	return $http.get('/api/registrations/',{params:query_params}).then(function(response){
		  		params.total(response.data.count);
		  		return response.data.results;
		  	});
	      }
	    });
	$scope.exportRegistrations = function(format){
		var url = '/api/registrations/export_registrations/?'+$httpParamSerializer($scope.registrationParameters)+'&export_format='+format;
		console.log('url',url);
		window.location = url;
	}
  }

