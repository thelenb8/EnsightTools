import os
import re
import shutil
import ensight
import numpy as np

# CONSTANT DECLARATIONS
CONVERGE_CELL_DATA = 'CONVERGE Cell Data' # constant in case the part name for CONVERGE Cell Data should change in the future
DEFAULT_ZOOM_LEVEL = 1.5
LEGEND_FONT_NAME = 'Arial:Bold'
LEGEND_NUMBER_FORMAT = '%.0f'
LABEL_TEXT_SIZE = 20
DEFAULT_ZFILL = 4

class NoMatchFound(Exception):
    pass

# GENERIC FUNCTIONS
def find_in_list(target,list):
    '''Finds the index of the target in the list.'''

    for i, obj in enumerate(list):
        if obj == target:
            return i
    else:
        return None

def find_file_type(directory,regex):

    '''Finds a filename in a given directory that matches the provided regular
    expression.'''

    try_regex = re.compile(regex)

    file_list = os.listdir(directory)
    match_list = [ ]

    for file in file_list:
        if try_regex.search(file):
            match_list.append(file)


    if len(match_list) == 0:
        raise NoMatchFound('No files match %s' % regex)
    elif len(match_list) > 1:
        print 'There is more than one file that matches %s' % regex
        print 'Returning: %s' % match_list[0]
        print 'Also found:'
        for i in range(1,len(match_list)):
            print(match_list[i])

    return match_list[0]

def make_output_folder(directory,folder_name, delete_contents=False):
    ''' make_output_folder(directory,folder_name)

    DESCRIPTION: Checks to see if the provided directory has the folder
    specified. If it does, it deletes the contents within the folder. If it
    does not, then create the folder.

    INPUTS:
    directory: <str> Full path to the directory containing the data to be
               processed
    folder_name: <str> Name for the new folder to be placed in the given
                 directory

    OUTPUTS:
    None: File structure on the computer is modified.

    '''

    # Make the full path name for the new folder
    save_folder = directory + '/' + folder_name

    print "Checking for output directory:"
    print "  %s" % save_folder

    # Check to see if the folder exists and create it if it doesn't
    if not os.path.isdir(save_folder):
        print "Creating: %s" % save_folder
        os.makedirs(save_folder)
        print "The following directory exists and is empty:"

    else:
        print "%s Exists." % save_folder
        if delete_contents:
            files = os.listdir(save_folder)
            n = len(files)
            if n > 0:
                print "The directory is not empty."
                print "Removing the %d files" % n
                for file in files:
                    os.remove(save_folder + '/' + file)
                    print "The following directory exists and is empty:"
        else:
            print "The following directory exists:"


    print "  %s" % save_folder

    return save_folder

def sheep():

    print 'Bahh!'

# ENSIGHT FUNCTIONS
def load_case_file(directory):

    file_name = find_file_type(directory,'case$')

    to_load = directory + '/' + file_name

    print 'Loading the following:'
    print '%s' % to_load

    ensight.data.replace(to_load)

    print 'Loading Complete'

    return file_name

def find_converge_data():

    '''Return the part id number for the converge cell data part.'''

    sucess_code, part_numbers, part_name_list = ensight.query(ensight.PART_OBJECTS)


    index = find_in_list(CONVERGE_CELL_DATA,part_name_list) + 1 # add one, since the first

    part_number = part_numbers[index]

    print "%s is part id # %d" % (CONVERGE_CELL_DATA, part_number)

    return part_number

def black_background():

    print "Making the viewport background black."

    ensight.view.hidden_line("OFF")
    ensight.viewport.select_begin(0)
    ensight.viewport.background_type("constant")
    ensight.viewport.constant_rgb(0,0,0)
    ensight.viewport.select_end()

    print "Viewport modification are complete."

def hide_all_parts():

    print "Hiding all parts."

    # Determine how many part objects there are
    part_query = ensight.query(ensight.PART_OBJECTS)
    num_parts = part_query[1][0]

    print "There are %d parts." % num_parts

    # Cycle through the parts and hide them
    for i in range(0,num_parts):
        ensight.part.select_begin(i+1)
        ensight.part.visible("OFF")
        ensight.part.select_end()

    print "All %d parts are now hidden." % num_parts

def ortho_clip(clip_plane,clipped_part,offset):

    '''clip_part_id = ortho_clip(clip_plane,clipped_part,offset)

    DESCRIPTION: Generates an orthogonal clip in either the x, y, or z plane
                 through a given domain.

    INPUTS:
    clip_plane: <str> (X|Y|Z) this is the normal axis of the plane
    clipped_part: <int> this the part ID for the domain of data that is being
                  cut through
    offset: <float> Distance from the origin of the clip plane [m]

    OUTPUTS:
    clip_part_id: <int> this is the ensight part number id for the created clip
    '''
    #TODO: Make data verification for input types

    print ("Creating an ortho clip plane offset %1.3f m on the %s axis" %
           (offset,clip_plane))

    # Construct the clip
    ensight.part.select_begin(clipped_part)
    ensight.clip.begin()
    ensight.clip.mesh_plane(clip_plane)
    ensight.clip.tool('xyz')
    ensight.clip.value(offset)
    ensight.clip.end()
    ensight.clip.create()

    part_query = ensight.query(ensight.PART_OBJECTS) # Returns a list of values
                                                     # second item is a list containing [num_parts, id1, id2, id3, ...]
                                                     # third item is a list containing object names ['Measured/particle', 'CONVERGE Cell Data', 'Clip_plane', ...]

    clip_part_id = part_query[1][-1]

    print "Clip creation complete."

    return clip_part_id

def make_nodal_variable(var,domain_part_number):

    '''Interpolates the data for a given variable to calculate its values at
    nodal locations rather than cell centered to make nicer plots.


    Old, only function in DATA_CONVERT.py'''

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

    ensight.part.select_begin(domain_part_number)
    ensight.variables.evaluate(var_statement)

    if var_type == 0:
        ensight.ext.treecmd_treecmds_obj().cmdRun('create_group',{'pathid': [None], 'var': '', 'path': ['Scalars']})
        ensight.ext.treecmd_treecmds_obj().cmdRun('reparent_var',{'pathid': [None], 'var': new_var, 'path': ['Scalars']})

    if var_type == 1:
        ensight.ext.treecmd_treecmds_obj().cmdRun('create_group',{'pathid': [None], 'var': '', 'path': ['Vectors']})
        ensight.ext.treecmd_treecmds_obj().cmdRun('reparent_var',{'pathid': [None], 'var': new_var, 'path': ['Vectors']})


    return new_var

def calculate_progress_variable(part_number):

    print "Calculating Propane Progress Variable"
    ensight.part.select_begin(part_number)
    ensight.variables.evaluate("Z_CO2 = MASSFRAC_CO2/44.01")
    ensight.variables.evaluate("Z_C3H8 = MASSFRAC_C3H8/44.097")
    ensight.variables.evaluate("PROGRESS = 1-(Z_C3H8/(Z_C3H8+(1/3)*Z_CO2))")
    ensight.part.select_end()
    print "Calculation complete."

def color_part(part_id,variable):

    '''Instructs Ensight to color the given part id with the given variable.'''
    print "Coloring part id # %d with variable: %s" % (part_id, variable)

    ensight.part.select_begin(part_id)
    ensight.part.colorby_palette(variable)
    ensight.part.modify_end()

def ortho_adjust_view(axis,zoom_level=DEFAULT_ZOOM_LEVEL,axis_negate=True):

    '''Adjusts the viewport view for image making.'''

    print "Adjusting the view and zoom"

    ensight.viewport.select_begin(0)
    if axis_negate:
        ensight.view_transf.view_recall("-"+axis)
    else:
        ensight.view_transf.view_recall(axis)

    ensight.annotation.axis_model("OFF")

    ensight.viewport.select_end()

def colorbar_scale(variable,low,high,number_of_levels):

    '''Modifies the colorbar scale to the provided parameters.'''

    print "Adjusting the colorbar scale for %s." % variable

    ensight.function.palette(variable)
    ensight.function.modify_begin()
    ensight.function.range(low,high)
    ensight.function.number_of_levels(number_of_levels)
    ensight.function.modify_end()

def setup_legend(variable,title_string):

    '''Modifies the position and apperance of the legend.'''

    ensight.legend.select_palette_begin(variable)
    ensight.legend.text_size(40)
    ensight.legend.location_x(.85)
    ensight.legend.location_y(.22)
    ensight.legend.height(.5)
    ensight.legend.width(.05)

    title_str = "<fo=" + LEGEND_FONT_NAME + ">" + title_string
    ensight.legend.title_name(title_str)
    ensight.legend.format(LEGEND_NUMBER_FORMAT)
    ensight.legend.select_end()

def create_time_steps(start_time,end_time,time_step):

    print "Creating the time vector [%1.4f,%1.4f] with dt = %1.4f" % (start_time,end_time,time_step)

    t = start_time
    tsteps = [start_time]

    while t < end_time - time_step:
        t = t + time_step
        if t <= end_time:
            tsteps.append(t)

    print "There are %d time steps." % len(tsteps)

    return tsteps

def determine_number_of_steps(target_dt):

    time_limits = ensight.query(ensight.TIMEVALS)['timelimits']
    duration = time_limits[1] - time_limits[0]
    number_of_steps = round(duration/target_dt)


def create_image_label(step_number,directory,isBlack=False):
    '''Creates a label at the top and center of the viewport with the given step
    number, simulation time, and case directory.'''

    ensight.text.select_default()
    ensight.text.justification("center")
    ensight.text.size(LABEL_TEXT_SIZE)
    ensight.text.location_x(.5)
    ensight.text.location_y(.95)

    if isBlack:
        ensight.text.rgb(0,0,0) # Black text
    else:
        ensight.text.rgb(1,1,1) # Default behavior is white text

    step_str = str(step_number).zfill(DEFAULT_ZFILL)

    ensight.text.new_text(step_str + ': ' + r'<\\master_time "%.6e" \\> s -- %s' % directory)







# QUERY FUNCTIONS
def min_max_query(directory,case_name,variable,units,steps):

    '''Function that produces a text file containing the minimum and maximum
    values of a variable in the Converge cell data.'''

    print 'Starting Min/MAX query for %s for %s with %d steps.' % (case_name[:-5],variable,steps)

    # Find the start and end times of the simulation
    [start_time, end_time] = ensight.query(ensight.TIMEVALS)['timelimits']

    # Find the converge cell data part
    part_number = find_converge_data()

    # Activate the Variable
    ensight.variables.activate(variable)

    # Get the data from the maximum and minimum queries
    print 'Performing maximum value query for %s' % variable
    max_data = query_instructions(part_number,variable,'max',start_time,
                                  end_time,steps)

    print 'Performing minimum value query for %s' % variable
    min_data = query_instructions(part_number,variable,'min',start_time,
                                  end_time,steps)


    samples = len(min_data)/2
    max_data = np.reshape(max_data,(samples,2))
    min_data = np.reshape(min_data,(samples,2))
    min_max_data = np.zeros((samples,3))
    min_max_data[:,0] = max_data[:,0]
    min_max_data[:,1] = max_data[:,1]
    min_max_data[:,2] = min_data[:,1]

    print 'Exporting queries to text document'
    # Check to see if there is a query output directory
    folder_name = 'Queries'
    make_output_folder(directory,folder_name,delete_contents=False)
    output_folder = directory + '\\' + folder_name

    file_to_write = output_folder + '\\' + variable + '_Min-Max(%s)' % case_name[:-5] + '.txt'
    f = open(file_to_write,'w')

    f.write('Simulation: %s\n' % case_name[:-5])
    f.write('Variable: %s\n' % variable)
    f.write('Units: %s\n' % units)
    f.write('------------------------------------\n')
    f.write('Step\tTime(s)\tMaximum\tMinimum\n')
    f.write('=====\t========\t========\t========\n')

    for i in range(0,samples):
        step = str(i).zfill(3)
        f.write('%s\t%1.5e\t%1.5e\t%1.5e\n' % (step,min_max_data[i,0],
                                               min_max_data[i,1],
                                               min_max_data[i,2]))
    f.close()

def query_instructions(part_number,variable,constraint,start_time,end_time,
                       steps):

    # Make the description string
    if constraint == 'max':
        descript_str = 'Maximum %s' % variable
    elif constraint == 'min':
        descript_str = 'Minimum %s' % variable
    else:
        descript_str = '%s %s'% (constraint,variable)

    # Instruction set for the query
    ensight.part.select_begin(part_number)
    ensight.query_ent_var.begin()
    ensight.query_ent_var.description(descript_str)
    ensight.query_ent_var.query_type("generated")
    ensight.query_ent_var.number_of_sample_pts(steps)
    ensight.query_ent_var.begin_simtime(start_time)
    ensight.query_ent_var.end_simtime(end_time)
    ensight.query_ent_var.constrain(constraint)
    ensight.query_ent_var.sample_by("value")
    ensight.query_ent_var.variable_1(variable)
    ensight.query_ent_var.generate_over("time")
    ensight.query_ent_var.variable_2("TIME")
    ensight.query_ent_var.end()
    ensight.query_ent_var.query()

    # Retrieve the Query Data
    [trash, num_queries] = ensight.query(ensight.QUERY_COUNT)
    latest_query = num_queries[0]-1
    query_return = ensight.query(ensight.QUERY_DATA,latest_query)
    # Convert to a numpy array
    data = np.array(query_return[2])

    return data

# FUNCTIONS FOR SAVING DATA

def setup_image():

    ensight.file.image_format('tiff')
    ensight.file.image_format_options("Compression None")
    ensight.anim_recorders.render_offscreen("ON")
    ensight.file.image_numpasses(4)
    ensight.file.image_stereo("current")
    ensight.file.image_screen_tiling(1,1)

def time_step_output(output_directory,tsteps):

    print "Saving images to %s" % output_directory

    fid = open(output_directory + '/image_index.txt', 'w')
    fid.write("Image_#\t\tTime")
    fid.write(' [ ]   \t\t [s]\n')
    fid.write("-------\t\t----\n")


    # Change from simulations step numbers to continuous time
    ensight.solution_time.update_type("continuous")
    ensight.solution_time.show_as("time")


    for i,t in enumerate(tsteps):
        ensight.solution_time.current_simtime(t)
        ensight.solution_time.update_to_current()
        s = str(i).zfill(3)
        fid.write(" %s\t\t" % s)
        fid.write("%1.5f\t\t\n" % t)
        ct = ensight.query(ensight.TIMEVALS)['timecurrent']
        s2 = "{:10.4e}".format(ct)

        file_out = output_directory + '/' + s + ' (' + s2 + ')'

        print "Saving image %d: %s" % (i,file_out)

        ensight.file.image_file(file_out)
        ensight.file.save_image()

    fid.close()


# ROUTINES
def bulk_min_max_query(directory_list,variable_list,units_list,step_dt):

    print "Initiating bulk min_max_query for the following:"

    for sim in directory_list:
        print "%s" % sim

    print "...for the following variables:"

    for var in variable_list:
        print "%s" % var

    print "==================================="

    for sim in directory_list:
        print "Loading: %s" % sim

        try:
            # Load the case
            case_name = load_case_file(sim)

            # Determine the number of steps
            steps = determine_number_of_steps(step_dt)

            # Step through the variable list and make the queries
            for i in range(0,len(variable_list)):
                print "Query for variable: %s" % variable_list[i]
                min_max_query(sim,case_name,variable_list[i],units_list[i],steps)
        except:
            print "There was an error processing the data for:\n%s" % sim

























