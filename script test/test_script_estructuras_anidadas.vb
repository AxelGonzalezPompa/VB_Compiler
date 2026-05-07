Imports System

Module Program
    
    Sub Main()
        Dim x As Integer = 0
        While x < 5
            While x < 4
                x = 1
            End While
        End While
        
        Dim y As Integer = 0
        For y As Integer = 0 To 5 Step 1
            If y == 1 Then
                Print (y)
            End If
        Next
        
        For x As Integer = 0 To 5 Step 1
            If x == 1 Then
            Next
        End If                                                                
        
        Dim x As Integer
        For x As Integer = 0 To 5 Step 1 
            If x == 1
                Print (x)
            End If
        Next x
        
        Dim x As Integer
        (x = 0 To 5 Step 1 As Integer) For
            (x == 1) If Then
                x Print ();
        Next x
                                        
    End Sub
End Module





