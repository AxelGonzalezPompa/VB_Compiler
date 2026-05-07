Imports System

Module Program
    Dim x As Integer = 6
    Dim b As string
    Dim variable As Integer
    
    Sub Main()
        Dim x As Integer = 5
        Dim variable As String = "0"
        Dim b As Boolean = False
        Dim z As Integer = 4
        Dim c As Char
        x = (x + z) * 7 + (5)
        x = 2
        c = 'p'
        b = True
        variable = "hola soy un string"
        
        Dim puntaje As Integer = 85
        Dim bandera As Boolean

        Select Case puntaje
            Case 90 To 100
                bandera = True
            Case 70, 80, 85
                bandera = True
            Case Is < 60
                bandera = True
            Case Is < 60
                bandera = True
            Case Else
                bandera = False
        End Select
        
        Select Case puntaje
            Case To
                bandera = True
            Case 90 To 
                bandera = True
            Case 70, 80, 
                bandera = True
            Case , 80
                bandera = True
            Case Is < 
                bandera = True
            Case Is 60 
                bandera = True
            Case Else
                bandera = False
        End Select
        
        Select Case puntaje
            Case Else
                bandera = False
            Case 90 To 100
                bandera = True
        End Select
        
        Select Case puntaje
            Case Is < 60
                bandera = True
            Case Else
                bandera = False
        
        Select Case 
            Case Is < 60
                bandera = True
            Case Else
                bandera = False
        End Select
        
    End Sub
End Module




