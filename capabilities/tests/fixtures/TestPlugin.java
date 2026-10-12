import com.airdeck.decksdk.*;
import com.airdeck.capabilities.Media;
import java.util.List;
import java.util.concurrent.*;
public final class TestPlugin implements DeckPlugin,PluginHost.Initializer {
 private Media.Client client;
 public void init(PluginHost h){client=new Media.Client(h);}
 public List<Button> catalog(){return List.of();}
 public void invoke(String t,String a,String b,String p){if(a.equals("subscribe")){CompletableFuture<Media.Playback> state=new CompletableFuture<>();Runnable stop=client.subscribePlayback(v->state.complete(v));try{Media.Playback v=state.get(2,TimeUnit.SECONDS);if(v.status!=Media.PlaybackStatus.PLAYING||!v.available)throw new RuntimeException("wrong state");}catch(Exception e){throw new RuntimeException(e);}finally{stop.run();}return;}Media.Playback v=client.getPlayback(new Media.Empty());if(v.status!=Media.PlaybackStatus.PLAYING||!v.available)throw new RuntimeException("wrong typed response");}
 public static void main(String[] args)throws Exception{PluginHost.run(new TestPlugin());}
}
