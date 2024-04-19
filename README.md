# lmutil_lmremove
Python script to remove all users currently using nx_design_token features using flexlm's lmutil lmremove utility.
Example use case: If UserA pulls 25 token licenses because he accidentally switched on Additive Manufacturing, UserB may not be able to run the NX Routing application in order to do his work. The NX administrator can manage this as they come up, or UserB can run this utility to kick UserA off the token licenses temporarily and then grab them himself by launching NX Routing. UserA may get a license error once NX "hearbeats" the license server, but work should continue. 

-------------------------------------------------------------------
The script:

-finds lmutil.exe either via the PATH or UGII_BASE_DIR environment variable
-finds SPLM_LICENSE_SERVER variable

-executes lmutil lmstat for nx_design_token users
-lists all current users
-gives user option to remove some or all of the users currently using the license

-lmutil lmremove is then executed one-by-one for selected user(s)

-script gives user the option to run it again to check users are now removed
----------------------------------------------------------------

-Juan
