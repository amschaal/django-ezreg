var app = angular.module('ezreg');
app.requires.push('ui.tinymce');

app.controller('DesignerController', function($scope,$http,Event) {
    $scope.field_types = [
                          {'class':'field','type':'text', 'label': 'Text Field'},
                          {'class':'field','type':'textarea', 'label': 'TextArea Field'},
                          //{'class':'field','type':'file', 'label': 'File Field'},
                          {'class':'field','type':'radio', 'label': 'Radio Field'},
                          {'class':'field','type':'integer', 'label': 'Integer Field'},
                          {'class':'field','type':'select', 'label': 'Select Field'},
                          {'class':'field','type':'checkbox', 'label': 'Checkbox Field'},
                          {'class':'field','type':'multicheckbox', 'label': 'Multiple Checkbox Field'},
                          {'class':'layout','type':'layout_html', 'label': 'HTML Label'}
                          ];
    
    $scope.fields=[];
    $scope.initialize = function(fields,event_id){
    		$scope.fields = fields;
    		$scope.event_id = event_id;
    };
    $scope.move = function(index,diff){
    	$scope.fields.splice(index+diff, 0, angular.copy($scope.fields.splice(index, 1)[0]));
    };
    $scope.save = function(){
    	var url = django_js_utils.urls.resolve('update_event_form', { event: $scope.event_id })
    	console.log('posting: ',$scope.event_id, $scope.fields);
    	$http.post(url,{form_fields:$scope.fields})
    	.success(function(){alert('The form has been updated.')})
    	.error(function(){alert('There was an error updating the form.')});
    };
    $scope.addField = function(){
    	$scope.fields.push({});
    };
    $scope.test = function(){
    	console.log($scope.fields);
    }
    $scope.addOption = function(field){
    	if (!field.choices)
    		field.choices = [];
    	field.choices.push({});
    }
    $scope.removeOption = function(field,index){
    	field.choices.splice(index,1);
    }
    $scope.removeField = function(index){
    	if(confirm('Are you sure you want to remove this field?'))
    		$scope.fields.splice(index,1);
    }
    $scope.getEvents = function(val) {
        return Event.query({serializer:'detailed',title__icontains:val}).$promise.then(function(response){
        	console.log('response',response);
        	return response;
        });
    }
    $scope.copyEventForm = function($item, $model, $label){
    	if ($item.form_fields){
    		$scope.fields = $scope.fields.concat($item.form_fields);
    		alert($item.form_fields.length+' fields have been copied.')
    	}
    	$scope.asyncSelected = '';
    }
  });