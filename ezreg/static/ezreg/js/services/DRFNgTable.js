angular.module('DRFNgTable',['ngTable','btorfs.multiselect'])

//Usage: $scope.tableParams = DRFNgTableParams('/api/users/',{sorting: { last_name: "asc" }});
.factory('DRFNgTableParams', ['NgTableParams','$http', function(NgTableParams,$http) {
	return function(url,ngparams,resource) {
		var params = {
//				page: 1, // show first page
//				filter:{foo:'bar'}, //filter stuff
				count: 10 // count per page
		}
		angular.merge(params,ngparams);
		return new NgTableParams(params, {
			filterDelay: 0,
			getData: function(params) {
				var url_params = params.url();
				var query_params = {page:url_params.page,page_size:url_params.count,ordering:params.orderBy().join(',').replace('+','')};
				angular.extend(query_params, params.filter());
				// ajax request to api
				return $http.get(url,{params:query_params}).then(function(response){
					params.total(response.data.count);
					if (resource)
						return response.data.results.map(function(obj){return new resource(obj);});
					else
						return response.data.results;
				});
			}
		});
	};
}])
.run(function($templateCache) {
  $templateCache.put('ng-table/filters/multi_select.html', '<multiselect ng-disabled="$filterRow.disabled" ng-model="params.filter()[name]" options="$column.data" show-select-all="true" show-unselect-all="true" id-as-value="true" id-prop="id" display-prop="title"></multiselect>');
});

//data.id as data.title for data in $column.data