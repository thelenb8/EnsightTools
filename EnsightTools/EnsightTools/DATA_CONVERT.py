def make_nodal(var):
	# Import Ensight
	import ensight
	
	varlist = ensight.query(ensight.VARIABLE_OBJECTS)[2]
	vartypes = ensight.query(ensight.VARIABLE_OBJECTS)[1]
	ensight.variables.activate(var)
	print varlist

	# Find var in the variable list
	for i in range(0,len(varlist)):
		print i
		strd = varlist[i]
		print strd
		if strd == var:
			print "It's a match"
			var_num = i
			

	var_type = vartypes[var_num+1]
	print var_type

	# Construct new variable statement
	new_var = var + '_nodal'
	print "----------------------"
	print new_var
	var_statement = new_var + " = ElemToNode(plist," + var + ")"
	print var_statement

	ensight.part.select_begin(2)
	ensight.variables.evaluate(var_statement)

	if var_type == 0:
		ensight.ext.treecmd_treecmds_obj().cmdRun('create_group',{'pathid': [None], 'var': '', 'path': ['Scalars']})
		ensight.ext.treecmd_treecmds_obj().cmdRun('reparent_var',{'pathid': [None], 'var': new_var, 'path': ['Scalars']})
		
	if var_type == 1:
		ensight.ext.treecmd_treecmds_obj().cmdRun('create_group',{'pathid': [None], 'var': '', 'path': ['Vectors']})
		ensight.ext.treecmd_treecmds_obj().cmdRun('reparent_var',{'pathid': [None], 'var': new_var, 'path': ['Vectors']})