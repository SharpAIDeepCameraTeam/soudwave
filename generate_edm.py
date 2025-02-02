import os
import tensorflow as tf
import note_seq
from flask import Flask, jsonify, send_file, render_template
from magenta.models.drums_rnn import drums_rnn_sequence_generator
from magenta.models.music_vae import configs
from magenta.models.music_vae.trained_model import TrainedModel
from magenta.music import midi_io, sequences_lib, constants
from magenta.protobuf import generator_pb2, music_pb2

app = Flask(__name__)

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download')
def download_midi():
    output_file = os.path.join(os.environ.get('OUTPUT_DIR', '.'), 'futuristic_edm.mid')
    return send_file(output_file, as_attachment=True)

def create_buildup_sequence(sequence, steps=16):
    """Create a tension-building sequence by gradually increasing velocity and density"""
    for note in sequence.notes:
        # Increase velocity over time
        position_factor = note.start_time / sequence.total_time
        note.velocity = min(127, int(note.velocity * (1 + position_factor)))
    return sequence

def generate_drum_sequence(num_steps=128, temperature=1.0):  # Increased steps for 30 seconds
    """Generate EDM drum patterns with kick on every quarter note"""
    bundle_path = os.path.join(os.path.dirname(__file__), 
                              'magenta-main/magenta/models/drums_rnn/drum_kit_rnn.mag')
    bundle = note_seq.sequence_generator_bundle.read_bundle_file(bundle_path)
    
    generator_map = drums_rnn_sequence_generator.get_generator_map()
    generator = generator_map['drum_kit'](checkpoint=None, bundle=bundle)
    generator.initialize()

    generator_options = generator_pb2.GeneratorOptions()
    generator_options.args['temperature'].float_value = temperature
    generator_options.generate_sections.add(
        start_time=0,
        end_time=8)  # 8 bars for 30 seconds at 128 BPM

    sequence = generator.generate(music_pb2.NoteSequence(), generator_options)
    
    # Add consistent kick drum pattern (EDM style)
    for i in range(0, 8):  # 8 bars
        time = i * constants.QUARTER_STEPS / 4.0
        note = sequence.notes.add()
        note.pitch = 36  # Kick drum
        note.start_time = time
        note.end_time = time + 0.1
        note.velocity = 100
        note.instrument = 9  # Drum program
        note.is_drum = True
    
    return sequence

def generate_melody_sequence(num_bars=8):  # Increased bars for 30 seconds
    """Generate EDM-style melody with buildup"""
    checkpoint_path = os.path.join(os.path.dirname(__file__),
                                 'magenta-main/magenta/models/music_vae/checkpoints/mel_2bar_big.ckpt')
    config = configs.CONFIG_MAP['cat-mel_2bar_big']
    model = TrainedModel(config, batch_size=4, checkpoint_dir_or_path=checkpoint_path)

    z = model.sample(1)
    melodies = model.decode(z, length=num_bars)
    melody_sequence = melodies[0]
    
    # Add tension buildup
    melody_sequence = create_buildup_sequence(melody_sequence)
    return melody_sequence

def create_edm_track():
    """Create a 30-second EDM track with buildup and drop"""
    # Generate main sections
    drum_sequence = generate_drum_sequence()
    melody_sequence = generate_melody_sequence()
    
    # Combine sequences
    combined_sequence = music_pb2.NoteSequence()
    combined_sequence.MergeFrom(drum_sequence)
    for note in melody_sequence.notes:
        new_note = combined_sequence.notes.add()
        new_note.MergeFrom(note)
    
    # Set tempo to 128 BPM (standard EDM tempo)
    tempo = combined_sequence.tempos.add()
    tempo.qpm = 128
    
    # Quantize the final sequence
    quantized_sequence = sequences_lib.quantize_note_sequence(
        combined_sequence, steps_per_quarter=4)
    
    # Save as MIDI
    output_dir = os.environ.get('OUTPUT_DIR', '.')
    output_file = os.path.join(output_dir, 'futuristic_edm.mid')
    midi_io.note_sequence_to_midi_file(quantized_sequence, output_file)
    print(f"Generated EDM track saved as {output_file}")

if __name__ == '__main__':
    # Create output directory if it doesn't exist
    output_dir = os.environ.get('OUTPUT_DIR', '.')
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate the EDM track
    create_edm_track()
    
    # Run the Flask server
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
