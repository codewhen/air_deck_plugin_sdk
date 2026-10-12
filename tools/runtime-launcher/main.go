// Native Windows entrypoint for examples that require an interpreter.
package main

import (
 "fmt"
 "os"
 "os/exec"
 "path/filepath"
)

var language string

func main() {
 exe, err := os.Executable()
 if err != nil { fmt.Fprintln(os.Stderr, err); os.Exit(1) }
 dir := filepath.Dir(exe)
 var cmd *exec.Cmd
 switch language {
 case "python": cmd = exec.Command("python", filepath.Join(dir, "echo_plugin.py"))
 case "java": cmd = exec.Command("java", "-cp", filepath.Join(dir,"echo-plugin.jar")+string(os.PathListSeparator)+filepath.Join(dir,"gson.jar"), "com.example.echo.EchoPlugin")
 default: fmt.Fprintln(os.Stderr,"Unknown example runtime"); os.Exit(1)
 }
 cmd.Dir=dir; cmd.Stdin=os.Stdin; cmd.Stdout=os.Stdout; cmd.Stderr=os.Stderr
 if err := cmd.Run(); err != nil { fmt.Fprintln(os.Stderr,err); os.Exit(1) }
}
