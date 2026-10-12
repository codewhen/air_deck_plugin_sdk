// Native Windows entrypoint for examples that require an interpreter.
package main

import (
 "fmt"
 "os"
 "os/exec"
 "path/filepath"
)

var language string
var pythonEntry = "echo_plugin.py"
var javaMain = "com.example.echo.EchoPlugin"
var javaJar = "echo-plugin.jar"

func main() {
 exe, err := os.Executable()
 if err != nil { fmt.Fprintln(os.Stderr, err); os.Exit(1) }
 dir := filepath.Dir(exe)
 var cmd *exec.Cmd
 switch language {
 case "python": cmd = exec.Command("python", filepath.Join(dir, pythonEntry))
 case "java": cmd = exec.Command("java", "-cp", filepath.Join(dir,javaJar)+string(os.PathListSeparator)+filepath.Join(dir,"gson.jar"), javaMain)
 default: fmt.Fprintln(os.Stderr,"Unknown example runtime"); os.Exit(1)
 }
 cmd.Dir=dir; cmd.Stdin=os.Stdin; cmd.Stdout=os.Stdout; cmd.Stderr=os.Stderr
 if err := cmd.Run(); err != nil { fmt.Fprintln(os.Stderr,err); os.Exit(1) }
}
