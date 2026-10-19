!--------------------------------------------------------------------------------
! receive_lunch_items.f90
! Component of:
!     https://github.com/GhubGateway/Ghub_Pegasus_WMS_Tutorial_and_Templates and
!     https://theghub.org/tools/ghubex1
! Executable called from: Fortran_Launch.sh
! Also see Ghub, https://theghub.org/about
!--------------------------------------------------------------------------------

! In the Pegasus WMS YAML file,
! this job is specified to have the f.a input file and the f.b output file

program receive_lunch_items
    
    integer,parameter :: MAXSTRLEN=512
    CHARACTER(LEN=MAXSTRLEN) :: username, lunch_items

    call getarg(1, username)

    ! f.a contains the received lunch items

    open(1, file='f.a', status='old')
    open(2, file='f.b', status='replace')
    
    read(1,'(A)') lunch_items
    write(2,'(5A)') 'Hello ', trim(username), '! Received lunch items: ', trim(lunch_items), '.'

    close(1)
    close(2)
    
    ! f.b contains the served lunch items

END program receive_lunch_items
