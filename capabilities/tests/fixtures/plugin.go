package main
import("context";"encoding/json";"fmt";"time";"github.com/codewhen/air_deck_plugin_sdk/deck-plugins/sdk/go/decksdk";"github.com/codewhen/air_deck_plugin_sdk/capabilities/generated/go/media")
type plugin struct{client *media.Client}
func(p *plugin)Init(h *decksdk.Host){p.client=media.NewClient(h)}
func(p *plugin)Catalog()[]decksdk.Button{return nil}
func(p *plugin)Invoke(_ string,action string,_ json.RawMessage,_ json.RawMessage)error{if action=="subscribe"{done:=make(chan bool,1);stop,err:=p.client.SubscribePlayback(context.Background(),func(v media.Playback){done<-v.Status==media.PlaybackStatusPlaying&&v.Available});if err!=nil{return err};defer stop();select{case ok:=<-done:if !ok{return fmt.Errorf("wrong state")};return nil;case<-time.After(time.Second):return fmt.Errorf("state timeout")}};v,err:=p.client.GetPlayback(context.Background(),media.Empty{});if err!=nil{return err};if v.Status!=media.PlaybackStatusPlaying||!v.Available{return fmt.Errorf("wrong typed response")};return nil}
func main(){decksdk.Run(&plugin{})}
